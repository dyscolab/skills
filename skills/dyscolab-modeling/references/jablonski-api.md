# Public API inventory: jablonski (0.4.0 and newer)

Use this to check that a name exists before you write code with it. When the installed
version differs, check the installed source instead
(`python -c "import jablonski.simulation as m; print(dir(m))"`). The poincare inventory is
in [api-inventory.md](api-inventory.md).

Single-file modules (for example `jablonski.transitions` or `jablonski.simulation`) are part
of the public API just like package `__init__` exports.

Names marked *(newer)* exist only after jablonski 0.4.0.

## jablonski

| Module | Names | Reference |
| --- | --- | --- |
| `jablonski` | `SpectroscopicSystem`, `SingletState`, `TripletState`, `ConstantGroundState` *(newer)*, `initial`, `Parameter`, `assign`, `Simulator`, `pump_from_laser`, submodules `transitions`, `simulation`, `sweeps`, `util` | [jablonski.md](jablonski.md) |
| `jablonski.states` | `SpinState`, `SingletState`, `TripletState`, `initial`, `SpectroscopicSystem`; *(newer)* `ConstantGroundState`, `SingletStateLike`, `TripletStateLike`, `SpinStateLike` | [jablonski.md](jablonski.md#states) |
| `jablonski.transitions` | `Absorption`, `TripletTripletAbsorption`, `Fluorescence`, `Phosphorescence`, `InternalConversion`, `VibrationalRelaxation`, `IntersystemCrossing`, `ReverseIntersystemCrossing`, `EnergyTransferUpconversion` (0.4.0: three states; newer: the four-state transfer), `EnergyTransferUpconversion4` (0.4.0 only), `TripletTripletAnnihilation` (newer than 0.4.0), `check_all` (broken in 0.4.0) | [jablonski.md](jablonski.md#transitions) |
| `jablonski.simulation` | `piecewise`, `step_excitation`, `pulse_excitation`, `delta_excitation`, `spectral_time_resolved_emission`, `time_resolved_emission`, `spectral_steady_state_emission`, `steady_state_emission`, `emission_spectra`, `widened_emission_spectra`, `excitation_emission_matrix`, `excitation_spectra`; *(newer)* `spectral_time_resolved`, `time_resolved`, `spectral_steady_state`, `steady_state`, `spectra`, `widened_spectra`, `quantum_yield`, `spectral_quantum_yield` | [jablonski.md](jablonski.md#simulation-workflows) |
| `jablonski.sweeps` | `sweep_emission_spectra`, `sweep_spectral_steady_state_emission`; *(newer)* `sweep_spectra`, `sweep_spectral_steady_state`, `sweep_quantum_yield` | [jablonski.md](jablonski.md#sweeps) |
| `jablonski.fits` *(newer)* | `fit_spectral_time_resolved`, `make_time_resolved_target`, `fit_spectra`, `make_spectra_target`, `fit_spectral_time_resolved_emission`, `make_time_resolved_emission_target`, `fit_emission_spectra` | [jablonski.md](jablonski.md#fits) |
| `jablonski.util` | `SpectraKind`; 0.4.0: `emission_transitions`, `excitation_transitions`; *(newer)* `yield_transitions`, `lines_and_transform` | [jablonski.md](jablonski.md#plots-reports-and-helpers) |
| `jablonski.helpers` | `pump_from_laser`, `h`, `c` | same |
| `jablonski.plots` | `jablonski_diagram`, `graph_spectra`, `model_report`, `notebook_report` *(newer)* | same |
| `jablonski.rebop` | `RebopSimulator`, `rebop_piecewise`; *(newer)* `rebop_spectral_time_resolved`, `rebop_time_resolved`, `rebop_spectral_time_resolved_emission`, `rebop_time_resolved_emission` | [jablonski.md](jablonski.md#stochastic-runs) |
| `jablonski.skill` *(newer)* | `install`, `check`: the same as `poincare.skill` | [SKILL.md](../SKILL.md#versions-and-environment) |

## Internal helpers (don't use)

`jablonski.simulation.lines_to_energies`, `jablonski.util.TYPE_MAP` / `REVERSE_TYPE_MAP`,
`jablonski.fits.Time` (a re-exported type alias), `jablonski.rebop.rebop.distribute_points`,
`jablonski.plots.plots.get_column`, `sort_by_multiplicity`, `jablonski_diagram_section`,
`jablonski_diagram_markdown`, `color_code_etu`, `jablonski.util.convert` (dead code: it
references undefined names), and anything whose name starts with `_`.

## Not available in 0.4.0

Don't look for these in jablonski 0.4.0. Use the documented alternative instead. The third
column says which newer versions add them.

| Missing in 0.4.0 | Use instead | Newer versions |
| --- | --- | --- |
| A quantum-yield function | The transform recipe in [jablonski.md](jablonski.md#quantum-yields) | `quantum_yield`, `spectral_quantum_yield`, `sweep_quantum_yield` |
| Absorption spectra / `kind="absorption"` | `Absorption.absorption.rate_law` as a transform | `kind="absorption"` and lists of kinds |
| `jablonski.fits` | `poincare.analysis.fit_result` with jablonski transforms | `jablonski.fits` |
| A constant ground state | A state with a large population, or a `Parameter` in a custom transition | `ConstantGroundState` |
| `n_runs` on the rebop functions | A loop over seeds + `xr.concat(...).mean("run")` | `n_runs=` |
| Generic names (`time_resolved`, `steady_state`, `spectra`, …) | The `*_emission` functions (kept as wrappers in newer versions) | Generic names |
