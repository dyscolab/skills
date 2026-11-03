# jablonski 0.4: photophysical models

jablonski models are poincare `System`s built from electronic states and transitions.
`jablonski` re-exports `Simulator`, `Parameter` and `assign`. `initial` here is
jablonski's own state factory (it takes an energy). Import `SteadyState` and `solvers`
from `poincare`.

## Contents

- [States](#states)
- [Transitions](#transitions)
- [Custom transitions](#custom-transitions)
- [Composition](#composition)
- [Excitation](#excitation)
- [Simulation workflows](#simulation-workflows)
- [Quantum yields](#quantum-yields)
- [Sweeps](#sweeps)
- [Plots, reports and helpers](#plots-reports-and-helpers)
- [Stochastic runs](#stochastic-runs)

## States

```python
import pint
from jablonski import SpectroscopicSystem, SingletState, TripletState, Parameter, assign, initial
u = pint.get_application_registry()

class Dye(SpectroscopicSystem):
    S0: SingletState = initial(0 * u.eV, "singlet", default=1)    # energy, multiplicity, population
    S1: SingletState = initial(450 * u.nm, default=0)              # wavelength → eV
    T1: TripletState = initial(2.1, "triplet", default=0)          # bare float = eV
```

- `initial(energy, spin_multiplicity="singlet" | "triplet" | None, *, default=population)`.
  - The energy may be an energy, wavelength, wavenumber or frequency. It is stored in eV
    as `Dye.S1.energy`.
  - **A zero energy must be `0 * u.eV` (or `0`)**, because `0 / u.cm` raises
    `ZeroDivisionError`.
- Populations are usually unitless. Choose one normalisation and say which in a comment:
  - *Fraction of molecules* (each molecule's states sum to 1) suits single chromophores.
    Rates are 1/s.
  - *Fraction of all sites* (for example Yb states sum to 0.18 and Er to 0.02) suits doped
    crystals. Bimolecular transfer rates are then `W [cm³/s] × site density [cm⁻³]`.
  - Defaults can be parameter expressions (`default=yb_fraction`) so that composition is
    one parameter.
- `SpectroscopicSystem` defines `time` in seconds, so every time argument needs units.

## Transitions

Each transition is a small `SpectroscopicSystem` that wraps a `MassAction`. Pass states
by keyword. **States are declared from source to target.** Rates are `Parameter`s or
quantities.

| Transition | States (keywords) | `rate` units | Inner reaction attribute | Checks when the class is created |
| --- | --- | --- | --- | --- |
| `Absorption` | `ground`, `excited` (singlets) | cm² (cross-section); also `pump` in 1/(cm² s) | `absorption` | E(excited) ≥ E(ground) |
| `TripletTripletAbsorption` | `ground`, `excited` (triplets) | cm²; `pump` | `absorption` | as above |
| `Fluorescence` | `excited`, `ground` | 1/s | `radiative_decay` | E(excited) > E(ground), same multiplicity |
| `Phosphorescence` | `excited`, `ground` | 1/s | `radiative_decay` | E(excited) > E(ground), different multiplicity |
| `InternalConversion` | `high`, `low` | 1/s | `non_radiative_decay` | E(high) ≥ E(low), same multiplicity |
| `VibrationalRelaxation` | `high`, `low` | 1/s | `non_radiative_decay` | as above |
| `IntersystemCrossing` | `source` (singlet), `target` (triplet) | 1/s | `non_radiative_transition` | E(source) ≥ E(target) |
| `ReverseIntersystemCrossing` | `source` (triplet), `target` (singlet) | 1/s | `non_radiative_transition` | E(source) ≥ E(target) |
| `EnergyTransferUpconversion` | `sensitizer`, `activator`, `relaxator` | 1/s | `upconversion` | 2·E(sens) ≥ E(act) + E(relax); reaction 2·sens → act + relax |
| `EnergyTransferUpconversion4` | `sensitizer_high`, `sensitizer_low`, `activator_low`, `activator_high` | 1/s | `upconversion` | E(sh) + E(al) ≥ E(sl) + E(ah) |

- **Non-radiative triplet → singlet decay (T₁ → S₀)** uses `ReverseIntersystemCrossing`
  (triplet `source` → any lower singlet `target`). `InternalConversion` requires equal
  multiplicities.
- Physical checks raise `ValueError` or `TypeError` when the class is created. Don't
  work around them by swapping states. Use the transition that matches the physics, or a
  custom transition.
- `Absorption.pump` defaults to 0. Set it with excitation helpers, `with_values`, or an
  expression: `Absorption(..., pump=photon_flux)`, where `photon_flux` is a derived
  attribute.
- Every transition has an `energy_difference` property. For radiative transitions it is
  the photon energy, and for ETUs it is the energy released.
- `jablonski.transitions.check_all(Model)` warns about rates outside typical ranges. Some
  of those ranges are unreliable in 0.4.0, so treat the warnings as hints.
- **Bimolecular rates** (ETU, cross-relaxation) multiply two populations. If populations
  are fractions of sites, fold the site density into `rate` (for example
  `rate=k_cm3_per_s * site_density`).

## Custom transitions

Write one when a process needs another rate law (temperature dependence,
phonon-assisted or endothermic transfer, saturation):

```python
from symbolite import real
from poincare.reactions import MassAction
from jablonski.transitions import InternalConversion

class ThermalExcitation(SpectroscopicSystem):
    """Upward transfer source → target with k(T) = rate · exp(-gap / kT)."""
    source: SingletState = initial(0 * u.eV, default=0)
    target: SingletState = initial(0 * u.eV, default=0)
    rate: Parameter = assign(default=0 / u.s)
    T: Parameter = assign(default=300 * u.K)
    gap: Parameter = assign(default=0 * u.eV)
    kB: Parameter = assign(default=1 * u.boltzmann_constant)  # constants go in Parameters
    up = MassAction(reactants=[source], products=[target],
                    rate=rate * real.exp(-gap / (kB * T)))

class Model(SpectroscopicSystem):
    T: Parameter = assign(default=300 * u.K)
    a: SingletState = initial(2.0, default=1)
    b: SingletState = initial(2.1, default=0)
    down = InternalConversion(high=b, low=a, rate=1e6 / u.s)
    up = ThermalExcitation(source=a, target=b, rate=1e6 / u.s, T=T, gap=0.1 * u.eV)
```

- Use `symbolite.real` functions (`exp`, `expm1`, `log`, …), not numpy.
- **Pint constants written inline in the rate expression do not compile.** Put them in a
  `Parameter` as shown above.
- Link shared parameters such as temperature (`T=T`) so that one `with_values` changes
  every transition.
- To make a custom **radiative** transition count as an emission line, subclass
  `Fluorescence` or `Phosphorescence` (or reuse them). In 0.4.0, `emission_transitions`
  only finds those classes and reads `radiative_decay.rate_law` and `energy_difference`.
- Custom transitions are not drawn in `jablonski_diagram` unless they define
  `_source`/`_target` (set them in `__init__` after `super().__init__`).

## Composition

```python
class Pair(SpectroscopicSystem):
    ru = Ruthenium()          # complete molecule models as subsystems
    os = Osmium()
    transfer = InternalConversion(high=ru.MLCT_3, low=os.MLCT_3, rate=2.2e8 / u.s)
```

Refer to nested components as `Pair.ru.abs` and `Pair.ru.MLCT_3`.

## Excitation

An **excitation** is a mapping `{pumper_transition: photon_flux}`, for example
`{Dye.absorption: 1e20 / (u.cm**2 * u.s)}`. Time-dependent excitation is a set of
**events** `{time: {component: value}}` that `piecewise` applies.

```python
from jablonski.simulation import step_excitation, pulse_excitation, delta_excitation, piecewise

step = step_excitation({Dye.absorption: flux}, start=1 * u.ns)
pulse = pulse_excitation({Dye.absorption: flux}, width=5 * u.ns, start=1 * u.ns)
delta = delta_excitation(Dye.absorption, area=1e14 / u.cm**2, start=1 * u.ns)  # 50 ps pulse
result = piecewise(sim, events=pulse | delta, save_at=np.linspace(0, 50, 501) * u.ns)
```

- `delta_excitation` is a fixed 50 ps square pulse. For a shorter (or longer) pulse, use
  `pulse_excitation({pumper: area / width}, width=width, start=...)`. Keep the width short
  compared with the fastest process you want to resolve.
- `save_at` only sets the output points. The solver chooses its own steps, so accuracy
  depends on `rtol`/`atol`, not on the grid spacing.
- Event values may set **any parameter or variable**, not only pumps (power density,
  temperature, a rate). `None` restores the default.
- Event times and `save_at` must be time quantities. Event times are added to the output
  time grid.
- **jablonski 0.4.0 bug: an event at exactly `t = 0` is applied one segment late.** Start
  events at a small positive time (`start=1 * u.ps`). For excitation that is on from the
  start, set it on the simulator: `sim.with_values({Dye.absorption.pump: flux})`.
- `jablonski.pump_from_laser(model, wavelength, linewidth, power, width)` returns an
  excitation for every pumper whose transition wavelength is within `linewidth` of the
  laser. The flux is computed at the centre of a Gaussian beam (`width` = standard
  deviation). Its units are unsimplified, so call `.to(1 / (u.cm**2 * u.s))` before
  printing them.

## Simulation workflows

All of these take a `Simulator` (not a model class) and return xarray objects with pint
units. In 0.4.0 they are named `*_emission`.

| Function | Returns |
| --- | --- |
| `piecewise(sim, events=, save_at=)` | populations (and transforms) over time |
| `spectral_time_resolved_emission(sim, excitation=events, save_at=, kind="emission", join_by_energy=False)` | one `line_<transition>` photon rate per emission line over time; `attrs` maps line → energy |
| `time_resolved_emission(sim, excitation=events, save_at=, kind=)` | total `emission` over time |
| `spectral_steady_state_emission(sim, excitation, kind=, join_by_energy=False)` | steady-state rate per line |
| `steady_state_emission(sim, excitation, kind=)` | total steady-state `emission` |
| `emission_spectra(sim, excitation, unit=u.nm, kind=)` | line intensities indexed by `wavelenght` (sic) |
| `widened_emission_spectra(sim, excitation, unit=, kind=, samples=np.linspace(380, 700, 1000), width=5)` | Gaussian-broadened spectrum |
| `excitation_emission_matrix(sim, height, unit=)` | emission spectrum for each pumper at flux `height` |
| `excitation_spectra(sim, emission, height, unit=)` | intensity at one emission wavelength per pumper |

- `kind` is `"emission"` (fluorescence + phosphorescence), `"fluorescence"` or
  `"phosphorescence"`.
- `join_by_energy=True` sums lines with equal photon energy, and the variables are then
  named by energy.
- Signals are photon **rates** (`rate_law` of each radiative transition, per unit
  population), not normalised intensities.
- 0.4.0 quirks:
  - The spectra functions (`emission_spectra`, `excitation_emission_matrix`,
    `excitation_spectra`, `sweep_emission_spectra`) label the *intensities* with the
    wavelength unit (for example nm). Treat the values as photons/s and dequantify.
  - The coordinate is spelled `wavelenght`.
  - `excitation_spectra(sim, emission=...)` needs a wavelength that exactly equals one of
    the matrix's `wavelenght` coordinate values (take it from
    `excitation_emission_matrix(...)`).
  - The steady-state results include an `event` column (0 means converged).
- For stiff photophysics, set `sim = Simulator(Model).with_solver(solvers.LSODA(rtol=1e-8, atol=...))`
  with `atol` well below the smallest population of interest.

## Quantum yields

0.4.0 has no quantum-yield function. Compute emitted/absorbed photon rates with transforms
at steady state under weak excitation:

```python
qy_sim = sim.with_transform({
    "absorbed": Dye.absorption.absorption.rate_law,
    "fluorescence": Dye.fluorescence.radiative_decay.rate_law,
})
ss = SteadyState().solve(qy_sim.with_values({Dye.absorption.pump: 1e18 / (u.cm**2 * u.s)}))
qy = (ss["fluorescence"] / ss["absorbed"]).pint.dequantify().item()
```

Check it against `k_r / Σk` for the emitting state.

## Sweeps

- `jablonski.sweeps.sweep_emission_spectra(sim, excitations=[...], keys=[...], unit=, kind=)`
  and `sweep_spectral_steady_state_emission(sim, excitations=[...], keys=[...], kind=, join_by_energy=)`
  sweep over a list of excitations. `keys` labels each one (required when an excitation has
  more than one pumper).
- For power, temperature or rate sweeps of any output, use the loop pattern from
  [analysis.md](analysis.md#parameter-sweeps):
  `xr.concat([SteadyState().solve(sim.with_values({M.T: T})).isel(time=-1) for T in Ts], dim="T")`.
- `SteadyState().sweep` works on jablonski models (populations are unitless), but only
  returns populations.

## Plots, reports and helpers

- `jablonski.plots.jablonski_diagram(Model, figsize=, fontsize=, show_energy_axis=True, unit=u.eV)`
  returns `(fig, ax)`, with singlets and triplets in separate columns.
- `jablonski.plots.graph_spectra(sim, excitation, unit=, kind=, samples=, width=)` plots a
  wavelength-coloured broadened spectrum.
- `jablonski.plots.model_report(Model, path=None, ...)` gives a LaTeX report with a
  Jablonski diagram (PGF) as the first section.
- `jablonski.plots.notebook_report(Model, show=True, ...)` is the notebook version (Jupyter
  or marimo): the Jablonski diagram as an embedded PNG image, then equations, variables
  and parameters (same arguments as `poincare.printing.notebook_report`). Requires
  jablonski and poincare newer than the current PyPI releases.
- `jablonski.util.emission_transitions(Model, kind=)` and `excitation_transitions(Model)`
  yield the radiative and pumped transitions.
- `jablonski.helpers.h` and `c` are the Planck constant and speed of light as quantities
  (`h * c / λ` is the photon energy).

## Stochastic runs

```python
from jablonski.rebop import RebopSimulator, rebop_piecewise

rsim = RebopSimulator(Model)   # populations become integer molecule counts
ds = rebop_piecewise(rsim, events=pulse, upto_t=100 * u.ns, n_points=1000, rng=1)
```

Average many seeds before comparing with `piecewise`. Population defaults are truncated to
integers (molecule counts), so use counts such as 100, not fractions.
