"""Minimal Yb/Er energy-transfer upconversion model in jablonski.

Shows the conventions of larger photophysics models:
- literature-style parameters with units, one place to change them
- a derived pump (photon flux from power density and wavelength)
- energy transfer between ions with EnergyTransferUpconversion4
- a CW power sweep with SteadyState (loop + xr.concat)
- a laser pulse switched on and off with `piecewise` events on any parameter

Checks: ion populations are conserved, and green emission scales as P² at low
power (two-photon process), with a smaller slope at high power (saturation).
"""

import numpy as np
import pint
import xarray as xr

from jablonski import Parameter, Simulator, SingletState, SpectroscopicSystem, assign, initial
from jablonski.helpers import c, h
from jablonski.simulation import piecewise
from jablonski.transitions import (
    Absorption,
    EnergyTransferUpconversion4,
    Fluorescence,
    InternalConversion,
)
from poincare import SteadyState, solvers

u = pint.get_application_registry()


class YbEr(SpectroscopicSystem):
    # Excitation (control parameters)
    power_density: Parameter = assign(default=0 * u.W / u.cm**2)
    wavelength: Parameter = assign(default=980 * u.nm)
    photon_flux = power_density / (h * c / wavelength)  # derived, not a free parameter

    # Rates (illustrative values)
    yb_cross_section: Parameter = assign(default=1e-20 * u.cm**2)
    k_yb: Parameter = assign(default=1e3 / u.s)  # Yb 2F5/2 decay
    k_etu1: Parameter = assign(default=1e4 / u.s)  # Yb* + Er(4I15/2) -> Yb + Er(4I11/2)
    k_etu2: Parameter = assign(default=1e4 / u.s)  # Yb* + Er(4I11/2) -> Yb + Er(4F7/2)
    k_er3: Parameter = assign(default=1e3 / u.s)  # 4I11/2 decay (~1 µm emission)
    k_relax: Parameter = assign(default=1e7 / u.s)  # 4F7/2 -> 4S3/2 multiphonon relaxation
    k_green: Parameter = assign(default=2e3 / u.s)  # 4S3/2 -> 4I15/2 (~545 nm)

    # States: energies with units (wavenumbers here; zero energy must be given
    # in eV, a zero wavenumber fails to convert); populations are fractions of
    # all ion sites (18 % Yb, 2 % Er).
    Yb1: SingletState = initial(0 * u.eV, default=0.18)
    Yb2: SingletState = initial(10200 / u.cm, default=0)
    Er1: SingletState = initial(0 * u.eV, default=0.02)
    Er3: SingletState = initial(10200 / u.cm, default=0)
    Er6: SingletState = initial(18300 / u.cm, default=0)
    Er7: SingletState = initial(20400 / u.cm, default=0)

    yb_absorption = Absorption(ground=Yb1, excited=Yb2, rate=yb_cross_section, pump=photon_flux)
    yb_decay = Fluorescence(excited=Yb2, ground=Yb1, rate=k_yb)
    # EnergyTransferUpconversion4 requires E(sens_high) + E(act_low) >= E(sens_low) + E(act_high);
    # endothermic (phonon-assisted) transfers need a custom transition (see references/jablonski.md).
    etu1 = EnergyTransferUpconversion4(
        sensitizer_high=Yb2, sensitizer_low=Yb1, activator_low=Er1, activator_high=Er3, rate=k_etu1
    )
    etu2 = EnergyTransferUpconversion4(
        sensitizer_high=Yb2, sensitizer_low=Yb1, activator_low=Er3, activator_high=Er7, rate=k_etu2
    )
    er3_decay = Fluorescence(excited=Er3, ground=Er1, rate=k_er3)
    relaxation = InternalConversion(high=Er7, low=Er6, rate=k_relax)
    green = Fluorescence(excited=Er6, ground=Er1, rate=k_green)


sim = Simulator(YbEr).with_solver(solvers.LSODA(rtol=1e-10, atol=1e-16))

# CW power sweep. Transforms with append=True keep the populations in the output.
cw = sim.with_transform({"green": YbEr.green.radiative_decay.rate_law}, append=True)
powers = np.logspace(-1, 4, 11) * u.W / u.cm**2
sweep = xr.concat(
    [SteadyState().solve(cw.with_values({YbEr.power_density: p})).isel(time=-1) for p in powers],
    dim="power_density",
).assign_coords(power_density=powers.magnitude)

green = sweep["green"].pint.dequantify().values
slopes = np.diff(np.log(green)) / np.diff(np.log(powers.magnitude))
np.testing.assert_allclose(slopes[0], 2, atol=0.02)  # two-photon process
assert slopes[-1] < 1.5  # saturation at high power

# 1 ms laser pulse at 100 W/cm², starting at 0.1 ms. Event values may be any
# parameter; None restores the parameter's default.
events = {
    0.1 * u.ms: {YbEr.power_density: 100 * u.W / u.cm**2},
    1.1 * u.ms: {YbEr.power_density: None},
}
pulse = piecewise(cw, events=events, save_at=np.linspace(0, 5, 501) * u.ms).pint.dequantify()
np.testing.assert_allclose(pulse["Yb1"] + pulse["Yb2"], 0.18, rtol=1e-8)
np.testing.assert_allclose(pulse["Er1"] + pulse["Er3"] + pulse["Er6"] + pulse["Er7"], 0.02, rtol=1e-8)
assert pulse["green"].idxmax().item() > 1.1e-3  # ETU: green keeps rising after the pulse ends

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    sweep["green"].pint.dequantify().plot(xscale="log", yscale="log")
    plt.figure()
    pulse[["green"]].to_dataframe().plot()
    plt.show()
