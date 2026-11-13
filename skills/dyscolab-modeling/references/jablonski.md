# jablonski 0.4: photophysical models

jablonski models are poincare `System`s built from electronic states and transitions.
`jablonski` re-exports `Simulator`, `Parameter` and `assign`. `initial` here is
jablonski's own state factory (it takes an energy). Import `SteadyState` and `solvers`
from `poincare`.

Notes marked **Newer than 0.4.0** describe jablonski `main`, which is not on PyPI yet.
Check the installed version before using them.

## Contents

- [States](#states)
- [Transitions](#transitions)
- [Custom transitions](#custom-transitions)
- [Composition](#composition)
- [Excitation](#excitation)
- [Simulation workflows](#simulation-workflows)
- [Quantum yields](#quantum-yields)
- [Sweeps](#sweeps)
- [Fits](#fits)
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
- **Newer than 0.4.0: `ConstantGroundState`** is a ground state whose population is held
  constant, for example a solvent or a large reservoir. It is a `Parameter`, not a
  variable, so it has no equation and does not appear in the results. Its `default`
  population enters the rate of every transition that uses it.

  ```python
  from jablonski import ConstantGroundState

  class Dye(SpectroscopicSystem):
      G: ConstantGroundState = ConstantGroundState(default=1, energy=0 * u.eV)  # float energy = eV
      S1: SingletState = initial(450 * u.nm, default=0)
      T1: TripletState = initial(2.1, "triplet", default=0)
      absorption = Absorption(ground=G, excited=S1, rate=1e-16 * u.cm**2)
      fluorescence = Fluorescence(excited=S1, ground=G, rate=2e8 / u.s)
      phosphorescence = Phosphorescence(excited=T1, ground=G, rate=1e4 / u.s)  # also allowed
  ```

  It can replace a singlet or a triplet in any transition and passes both multiplicity
  checks. It is drawn with the singlets in `jablonski_diagram`. The type aliases
  `SingletStateLike`, `TripletStateLike` and `SpinStateLike` (in `jablonski.states`)
  cover both kinds of state.

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
| `EnergyTransferUpconversion` (0.4.0) | `sensitizer`, `activator`, `relaxator` | 1/s | `upconversion` | 2·E(sens) ≥ E(act) + E(relax); reaction 2·sens → act + relax |
| `EnergyTransferUpconversion4` (0.4.0) | `sensitizer_high`, `sensitizer_low`, `activator_low`, `activator_high` | 1/s | `upconversion` | E(sh) + E(al) ≥ E(sl) + E(ah) |
| `TripletTripletAnnihilation` (newer than 0.4.0) | `triplet_1`, `triplet_2` (triplets), `singlet_1`, `singlet_2` (singlets) | 1/s | `annihilation` | E(t1) + E(t2) ≥ E(s1) + E(s2); reaction t1 + t2 → s1 + s2 |

- **Newer than 0.4.0, ETU renamed (breaking):** the four-state transition is called
  `EnergyTransferUpconversion` (same keywords as `EnergyTransferUpconversion4`), and
  `EnergyTransferUpconversion4` and the old three-state class are gone. It no longer checks
  energies, so endothermic transfers are accepted. Write the three-state case
  2·sens → act + relax as a custom transition. Code that must run on both versions:

  ```python
  try:   # jablonski 0.4.0
      from jablonski.transitions import EnergyTransferUpconversion4 as EnergyTransferUpconversion
  except ImportError:   # newer
      from jablonski.transitions import EnergyTransferUpconversion
  ```

- **Newer than 0.4.0, triplet-triplet annihilation:** `TripletTripletAnnihilation` is the
  mass-action reaction T + T → S + S with rate `rate * triplet_1 * triplet_2`. The four
  states may be different levels. Pass the same state twice for a homo-annihilation: the
  reaction then has stoichiometry 2 and the rate goes as T². For TTA upconversion
  (T₁ + T₁ → S₁ + S₀) the singlet S₁ may lie above T₁, as long as the totals satisfy
  2·E(T₁) ≥ E(S₁) + E(S₀):

  ```python
  tta = TripletTripletAnnihilation(
      triplet_1=T1, triplet_2=T1, singlet_1=S1, singlet_2=S0, rate=1e-3 / u.s
  )
  ```

  With populations as numbers of molecules, `rate` is in 1/s per molecule. In 0.4.0,
  write it as a custom transition wrapping `MassAction(reactants=[T1, T1], products=[S1, S0], rate=k)`.
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
- `jablonski.transitions.check_all(Model)` warns about rates outside typical ranges
  (rates in 1/s, absorption cross-sections in cm²). Treat the warnings as hints, because
  the ranges are rough. It is broken in 0.4.0
  (`AttributeError: 'Parameter' object has no attribute 'units'`), so call it only on newer
  versions. Rates given as expressions are not checked.
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
- To make a custom **radiative** transition count as an emission line:
  - **0.4.0:** subclass `Fluorescence` or `Phosphorescence` (or reuse them).
    `emission_transitions` only finds those classes and reads `radiative_decay.rate_law`
    and `energy_difference`.
  - **Newer than 0.4.0:** subclassing a concrete transition raises
    `TypeError: cannot subclass Fluorescence` (poincare now only allows subclassing
    abstract systems). Instead, any `SpectroscopicSystem` with a reaction attribute named
    `radiative_decay` and an `energy_difference` property counts as emission
    (`kind="emission"`). A system with `pump`, `absorption` and `energy_difference` counts
    as absorption. `kind="fluorescence"`/`"phosphorescence"` still only select the
    built-in classes.

  ```python
  class HotBand(SpectroscopicSystem):          # newer than 0.4.0
      excited: SingletState = initial(0 * u.eV, default=0)
      ground: SingletState = initial(0 * u.eV, default=0)
      rate: Parameter = assign(default=0 / u.s)
      radiative_decay = MassAction(reactants=[excited], products=[ground], rate=rate)

      @property
      def energy_difference(self):
          return self.excited.energy - self.ground.energy
  ```
- Custom transitions are not drawn in `jablonski_diagram` unless they define
  `_source`/`_target` (set them in `__init__` after `super().__init__`). Newer versions
  also accept lists of states there, paired element by element.

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
  start, set it on the simulator: `sim.with_values({Dye.absorption.pump: flux})`. Fixed
  in newer versions, which also handle events at the end of `save_at` and very short
  pulses. The small positive start works in both.
- The `time` coordinate of `piecewise` results is in seconds, whatever the unit of
  `save_at`.
- `jablonski.pump_from_laser(model, wavelength, linewidth, power, width)` returns an
  excitation for every pumper whose transition wavelength is within `linewidth` of the
  laser. The flux is computed at the centre of a Gaussian beam (`width` = standard
  deviation). Its units are unsimplified, so call `.to(1 / (u.cm**2 * u.s))` before
  printing them.

## Simulation workflows

All of these take a `Simulator` (not a model class) and return xarray objects with pint
units. In 0.4.0 they are named `*_emission`.

**Newer than 0.4.0:** the functions have generic names, because they also handle
absorption: `spectral_time_resolved`, `time_resolved`, `spectral_steady_state`,
`steady_state`, `spectra` and `widened_spectra`. The `*_emission` names in the table remain
as wrappers with the same arguments, so they work in both versions.

| Function | Returns |
| --- | --- |
| `piecewise(sim, events=, save_at=)` | populations (and transforms) over time |
| `spectral_time_resolved_emission(sim, excitation=events, save_at=, kind="emission", join_by_energy=False)` | one photon rate per emission line over time (`line_<transition>`; newer: `emission_<transition>`); `attrs` maps line → energy |
| `time_resolved_emission(sim, excitation=events, save_at=, kind=)` | total `emission` over time |
| `spectral_steady_state_emission(sim, excitation, kind=, join_by_energy=False)` | steady-state rate per line |
| `steady_state_emission(sim, excitation, kind=)` | total steady-state `emission` |
| `emission_spectra(sim, excitation, unit=u.nm, kind=)` | line intensities indexed by `wavelenght` (sic) |
| `widened_emission_spectra(sim, excitation, unit=, kind=, samples=np.linspace(380, 700, 1000), width=5)` | Gaussian-broadened spectrum |
| `excitation_emission_matrix(sim, height, unit=)` | emission spectrum for each pumper at flux `height` |
| `excitation_spectra(sim, emission, height, unit=)` | intensity at one emission wavelength per pumper |

- `kind` is `"emission"` (fluorescence + phosphorescence), `"fluorescence"` or
  `"phosphorescence"`. **Newer than 0.4.0:** also `"absorption"` (absorbed photon rate of
  each pumper), or a list of kinds such as `["absorption", "fluorescence"]`. The total of
  `time_resolved`/`steady_state` is named `absorption` for `kind="absorption"` and
  `emission` otherwise.
- **Per-line variable names differ between versions:** `line_<transition>` in 0.4.0, and
  `emission_<transition>` or `absorption_<transition>` in newer versions (for example
  `emission_fluorescence`). For code that runs on both, use the totals
  (`time_resolved_emission(..., kind="fluorescence")["emission"]`), or find the line by
  suffix: `next(k for k in ds.data_vars if k.endswith("fluorescence"))`.
- `join_by_energy=True` sums lines with equal photon energy, and the variables are then
  named by energy.
- Signals are photon **rates** (`rate_law` of each radiative transition, per unit
  population), not normalised intensities.
- The steady-state results include an `event` column (0 means converged).
- The spectra coordinate is spelled `wavelenght`, in every version.
- 0.4.0 quirks, fixed in newer versions:
  - The spectra functions (`emission_spectra`, `excitation_emission_matrix`,
    `excitation_spectra`, `sweep_emission_spectra`) label the *intensities* with the
    wavelength unit (for example nm). Treat the values as photons/s and dequantify.
    Newer versions give them photon-rate units (1/s).
  - `excitation_spectra(sim, emission=...)` needs a wavelength that exactly equals one of
    the matrix's `wavelenght` coordinate values (take it from
    `excitation_emission_matrix(...)`). Newer versions pick the nearest wavelength.
- For stiff photophysics, set `sim = Simulator(Model).with_solver(solvers.LSODA(rtol=1e-8, atol=...))`
  with `atol` well below the smallest population of interest.

## Quantum yields

**Newer than 0.4.0:** `jablonski.simulation` has steady-state quantum-yield functions:

```python
from jablonski.simulation import quantum_yield, spectral_quantum_yield
from jablonski.sweeps import sweep_quantum_yield

excitation = {Dye.absorption: 1e18 / (u.cm**2 * u.s)}
qy = quantum_yield(sim, excitation, kind="fluorescence").pint.dequantify().item()  # emitted / absorbed
fluxes = np.array([1e18, 1e19]) / (u.cm**2 * u.s)
per_line = spectral_quantum_yield(sim, excitation, unit=u.nm)      # indexed by `wavelenght`
vs_flux = sweep_quantum_yield(sim, [{Dye.absorption: f} for f in fluxes])  # `excitation` dim
```

- `kind` selects the emission (`"emission"`, `"fluorescence"`, `"phosphorescence"` or a
  list). `"absorption"` raises `ValueError`. Absorption always sums every pumper.
- `quantum_yield` returns a dimensionless `DataArray` with one `time` point. It is computed
  with `SteadyState`, so the solver tolerances matter (see
  [analysis.md](analysis.md#steady-states)).
- `sweep_quantum_yield` needs `keys=` when an excitation has more than one pumper. Otherwise
  the fluxes become the coordinate.

0.4.0 has no quantum-yield function. Compute emitted/absorbed photon rates with transforms
at steady state under weak excitation (this also works in newer versions):

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
  more than one pumper). **Newer than 0.4.0:** they are also available as `sweep_spectra`
  and `sweep_spectral_steady_state` (with the absorption `kind`s), plus
  `sweep_quantum_yield` ([Quantum yields](#quantum-yields)).
- For power, temperature or rate sweeps of any output, use the loop pattern from
  [analysis.md](analysis.md#parameter-sweeps):
  `xr.concat([SteadyState().solve(sim.with_values({M.T: T})).isel(time=-1) for T in Ts], dim="T")`.
- `SteadyState().sweep` works on jablonski models (populations are unitless), but only
  returns populations.

## Fits

Only when the user provides data. In 0.4.0, fit jablonski models with
`poincare.analysis.fit_result` and jablonski transforms ([analysis.md](analysis.md#fitting-parameters-to-data)).

**Newer than 0.4.0:** `jablonski.fits` wraps poincare's `Fitter` for spectroscopic data.
The results are poincare `FitResult`s (best values plus `.pcov`).

```python
from jablonski import fits

# Time-resolved emission after a pulse
target = fits.make_time_resolved_target(
    {Dye.fluorescence: counts / u.s},   # key: transition (or str); values: one per time
    save_at=t_data * u.ns,
)
fit = fits.fit_spectral_time_resolved(
    sim, target, excitation=pulse,      # pulse: piecewise events, as for the simulation
    p0={Dye.k_ic: (5e7 / u.s, 1e6 / u.s, 1e9 / u.s)},
)
fit[Dye.k_ic], fit.pcov[Dye.k_ic, Dye.k_ic]

# CW spectrum (line intensities at the line wavelengths)
spec = fits.make_spectra_target(wavelengths * u.nm, intensities / u.s)
fit = fits.fit_spectra(sim, spec, excitation={Dye.absorption: flux}, p0={...})
```

- The target keys are transitions, and the names follow the simulation output
  (`emission_<transition>`, or energies with `join_by_energy=True`).
- `fit_spectral_time_resolved` compares only the times in the target, not the extra event
  times that `piecewise` adds.
- Give spectra intensities with photon-rate units (1/s). Plain numbers are dimensionless
  and fail with `PintError: Unexpected units in spectra`.
- Spectra are matched by sorted position, not by wavelength, so the target needs one value
  per model line.
- `sigma=` (experimental errors in the target's form), `scale=` and extra
  `scipy.optimize.least_squares` keywords work as in poincare's `fit_result`.
  `fit_spectral_time_resolved_emission`, `make_time_resolved_emission_target` and
  `fit_emission_spectra` are wrappers for `kind="emission"`.

## Plots, reports and helpers

- `jablonski.plots.jablonski_diagram(Model, figsize=, fontsize=, show_energy_axis=True, unit=u.eV)`
  returns `(fig, ax)`, with singlets and triplets in separate columns. **Newer than
  0.4.0:** each subsystem gets its own columns. Energy transfer upconversions are drawn,
  colour-coded per transfer (`etu_colors=` takes a list of colours or a cycler).
- `jablonski.plots.graph_spectra(sim, excitation, unit=, kind=, samples=, width=)` plots a
  wavelength-coloured broadened spectrum.
- `jablonski.plots.model_report(Model, path=None, ...)` gives a LaTeX report with a
  Jablonski diagram (PGF) as the first section.
- `jablonski.plots.notebook_report(Model, show=True, ...)` is the notebook version (Jupyter
  or marimo): the Jablonski diagram as an embedded PNG image, then equations, variables
  and parameters (same arguments as `poincare.printing.notebook_report`). Requires
  jablonski and poincare newer than the current PyPI releases.
- `jablonski.util.emission_transitions(Model, kind=)` and `excitation_transitions(Model)`
  yield the radiative and pumped transitions (0.4.0). **Newer than 0.4.0** replaces both
  with `yield_transitions(Model, kind=)` (`kind="absorption"` for pumpers).
  `lines_and_transform(Model, kind=)` returns the `{line name: transition}` and
  `{line name: rate law}` mappings that the simulation functions use.
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

**Newer than 0.4.0:**

- `rebop_piecewise(..., n_runs=20)` averages 20 runs with independent random streams. An
  integer `rng` seed now feeds one generator shared by every segment and run. In 0.4.0 each
  segment reused the same seed, so average over seeds yourself.
- The output `time` is in the unit of `upto_t`.
- Stochastic photon counts: `rebop_spectral_time_resolved(rsim, excitation=events, upto_t=, n_points=, kind=, join_by_energy=, rng=, n_runs=)`
  and `rebop_time_resolved(...)` mirror the deterministic functions. The `*_emission` names
  are wrappers.
