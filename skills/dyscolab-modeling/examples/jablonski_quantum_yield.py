"""Three-level dye (S0, S1, T1) in jablonski: quantum yields and lifetime.

Checks:
- fluorescence QY = k_r / (k_r + k_ic + k_isc)
- phosphorescence QY = QY_isc * k_p / (k_p + k_nr)
- after a short pulse, S1 emission decays with tau = 1 / (k_r + k_ic + k_isc)
"""

import numpy as np
import pint

from jablonski import Parameter, Simulator, SingletState, SpectroscopicSystem, TripletState, assign, initial
from jablonski.simulation import (
    delta_excitation,
    spectral_steady_state_emission,
    spectral_time_resolved_emission,
)
from jablonski.transitions import (
    Absorption,
    Fluorescence,
    InternalConversion,
    IntersystemCrossing,
    Phosphorescence,
    ReverseIntersystemCrossing,
)
from poincare import SteadyState, solvers

u = pint.get_application_registry()


class Dye(SpectroscopicSystem):
    # initial(energy, multiplicity, default=population); a bare float energy is eV.
    S0: SingletState = initial(0 * u.eV, "singlet", default=1)
    S1: SingletState = initial(450 * u.nm, "singlet", default=0)
    T1: TripletState = initial(2.1 * u.eV, "triplet", default=0)

    k_r: Parameter = assign(default=2e8 / u.s)
    k_ic: Parameter = assign(default=5e7 / u.s)
    k_isc: Parameter = assign(default=2.5e8 / u.s)
    k_p: Parameter = assign(default=1e4 / u.s)
    k_nr: Parameter = assign(default=3e4 / u.s)

    absorption = Absorption(ground=S0, excited=S1, rate=1e-16 * u.cm**2)  # cross-section
    fluorescence = Fluorescence(excited=S1, ground=S0, rate=k_r)
    internal_conversion = InternalConversion(high=S1, low=S0, rate=k_ic)
    isc = IntersystemCrossing(source=S1, target=T1, rate=k_isc)
    phosphorescence = Phosphorescence(excited=T1, ground=S0, rate=k_p)
    triplet_decay = ReverseIntersystemCrossing(source=T1, target=S0, rate=k_nr)


sim = Simulator(Dye).with_solver(solvers.LSODA(rtol=1e-10, atol=1e-14))
weak_flux = 1e18 / (u.cm**2 * u.s)  # photons / (cm² s); far from saturation

k_r, k_ic, k_isc, k_p, k_nr = 2e8, 5e7, 2.5e8, 1e4, 3e4
qy_fluo = k_r / (k_r + k_ic + k_isc)
qy_phos = k_isc / (k_r + k_ic + k_isc) * k_p / (k_p + k_nr)

# Emission line rates at steady state (photons/s per molecule).
lines = spectral_steady_state_emission(sim, {Dye.absorption: weak_flux})
print({name: energy for name, energy in lines.attrs.items()})  # line -> photon energy

# Quantum yields: emitted / absorbed photon rates via transforms.
qy_sim = sim.with_transform(
    {
        "absorbed": Dye.absorption.absorption.rate_law,
        "fluorescence": Dye.fluorescence.radiative_decay.rate_law,
        "phosphorescence": Dye.phosphorescence.radiative_decay.rate_law,
    }
)
ss = SteadyState().solve(qy_sim.with_values({Dye.absorption.pump: weak_flux}))
absorbed = ss["absorbed"].pint.dequantify().item()
np.testing.assert_allclose(ss["fluorescence"].pint.dequantify().item() / absorbed, qy_fluo, rtol=1e-5)
np.testing.assert_allclose(ss["phosphorescence"].pint.dequantify().item() / absorbed, qy_phos, rtol=1e-5)

# Time-resolved emission after a short pulse. Start events after t = 0:
# jablonski 0.4.0 applies an event placed exactly at t = 0 one segment late.
pulse = delta_excitation(Dye.absorption, area=1e12 / u.cm**2, start=0.1 * u.ns)
save_at = np.linspace(0, 20, 401) * u.ns
tr = spectral_time_resolved_emission(sim, excitation=pulse, save_at=save_at)
fl = tr["line_fluorescence"].pint.dequantify()
t = fl["time"].values
late = t > 1e-9  # well after the 50 ps pulse
slope = np.polyfit(t[late], np.log(fl.values[late]), 1)[0]
np.testing.assert_allclose(-1 / slope, 1 / (k_r + k_ic + k_isc), rtol=1e-3)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from jablonski.plots import jablonski_diagram

    jablonski_diagram(Dye)
    tr.pint.dequantify().to_dataframe().plot(logy=True)
    plt.show()
