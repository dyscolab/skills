# Public API inventory (poincare 1.2.0, simbio 1.2.0, jablonski 0.4.0, and newer)

Use this to check that a name exists in these versions before you write code with it. When
the installed version differs, check the installed source instead
(`python -c "import jablonski.simulation as m; print(dir(m))"`).

Single-file modules (for example `jablonski.transitions` or `jablonski.simulation`) are part
of the public API just like package `__init__` exports.

Names marked *(newer)* exist only on the libraries' `main` branches, after poincare 1.2.0,
simbio 1.2.0 and jablonski 0.4.0, and are not on PyPI yet.

## poincare

| Module | Names | Reference |
| --- | --- | --- |
| `poincare` | `System`, `Variable`, `Derivative`, `Parameter`, `Constant`, `Independent`, `initial`, `assign`, `Simulator`, `SteadyState`, `Oscillations`, `model_report`, `strip_units` *(newer)* | [poincare.md](poincare.md) |
| `poincare.solvers` | `LSODA`, `RK23`, `RK45`, `DOP853`, `Radau`, `BDF` (and the `Solver` protocol) | [poincare.md](poincare.md#simulator) |
| `poincare.simulator` | `Simulator`, plus the `Components` type alias (Constant \| Parameter \| Variable \| Derivative) | [poincare.md](poincare.md#simulator) |
| `poincare.analysis` | `SteadyState`, `Oscillations`, `Sweeper`, `fit_result`; *(newer)* `Fitter`, `fit_steady_state`, `make_target` | [analysis.md](analysis.md) |
| `poincare.analysis.fits` | `fit_result` (1.2.0 only; newer in `poincare.analysis.fit_wrappers`), `make_target`; *(newer)* `Fitter`, `FitResult`, `Covariance`, `ToleranceWarning`, `CovarianceWarning` | [analysis.md](analysis.md#fitting-parameters-to-data) |
| `poincare.units` *(newer)* | `strip_units` | [units.md](units.md) |
| `poincare.reactions` | `Reactant`, `reaction_initial`, `RateLaw`, `MassAction`, `AbsoluteRateLaw` | [simbio.md](simbio.md#reactions) |
| `poincare.reactions.rebop` | `RebopSimulator` | [analysis.md](analysis.md#stochastic-simulation-rebop) |
| `poincare.printing.latex` | `model_report`, `latex_equations`, `parameter_table`, `variable_table`, `ToLatex` | [poincare.md](poincare.md#reports-and-introspection) |
| `poincare.printing` (newer than 1.2.0) | `notebook_report`, `default_notebook_sections`, `model_report`, `latex_equations`, `parameter_table`, `variable_table` | [poincare.md](poincare.md#reports-and-introspection) |
| `poincare.helpers` | `get_from`, `to_values` | [poincare.md](poincare.md#reports-and-introspection) |

## simbio

| Module | Names | Reference |
| --- | --- | --- |
| `simbio` | re-exports from poincare (`System`, `Variable`, `Parameter`, `Constant`, `Independent`, `Simulator`, `initial`, `assign`, `Reactant`, `reaction_initial`, `RateLaw`, `MassAction`, `AbsoluteRateLaw`) plus `Compartment`, `Species`, `Volume`, `amount`, `concentration`, `volume`, `reaction_amount`, `reaction_concentration`, `model_report`, `notebook_report` (newer than the PyPI release) | [simbio.md](simbio.md) |
| `simbio.reactions` (`.single`, `.compound`, `.enzymatic`) | `Creation`, `AutoCreation`, `Destruction`, `Conversion`, `Synthesis`, `Dissociation`, `ReversibleSynthesis`, `Equilibration`, `CatalyzeConvert`, `MichaelisMenten`, `MichaelisMentenEqApprox`, `MichaelisMentenQuasiSSAprox` | [simbio.md](simbio.md#reaction-motifs) |
| `simbio.io.sbml` | `load`, `loads` (Python ≥ 3.14 with 1.2.0) | [simbio.md](simbio.md#sbml-biomodels-and-mathml) |
| `simbio.io.biomodels` | `load` | same |
| `simbio.io.mathML` | `to_mathML`, `mathMLImporter` | same |
| `simbio.io.sbml.substitute_by_name` (newer: `simbio.io.substitute_by_name`) | `substitute_by_name` | same |
| `simbio.latex` | `latex_reactions` (*(newer)* `format=`), `model_report`, `notebook_report` *(newer)* | [simbio.md](simbio.md#graphs-reports-stochastic-runs) |
| `simbio.io.graph.networkx` | `graph`, `to_Variable_graph`, `to_reaction_graph` | [simbio.md](simbio.md#graphs-reports-stochastic-runs) |
| `simbio.rebop` | `RebopSimulator` | [analysis.md](analysis.md#stochastic-simulation-rebop) |

## jablonski

| Module | Names | Reference |
| --- | --- | --- |
| `jablonski` | `SpectroscopicSystem`, `SingletState`, `TripletState`, `ConstantGroundState` *(newer)*, `initial`, `Parameter`, `assign`, `Simulator`, `pump_from_laser`, submodules `transitions`, `simulation`, `sweeps`, `util` | [jablonski.md](jablonski.md) |
| `jablonski.states` | `SpinState`, `SingletState`, `TripletState`, `initial`, `SpectroscopicSystem`; *(newer)* `ConstantGroundState`, `SingletStateLike`, `TripletStateLike`, `SpinStateLike` | [jablonski.md](jablonski.md#states) |
| `jablonski.transitions` | `Absorption`, `TripletTripletAbsorption`, `Fluorescence`, `Phosphorescence`, `InternalConversion`, `VibrationalRelaxation`, `IntersystemCrossing`, `ReverseIntersystemCrossing`, `EnergyTransferUpconversion` (0.4.0: three states; newer: the four-state transfer), `EnergyTransferUpconversion4` (0.4.0 only), `check_all` (broken in 0.4.0) | [jablonski.md](jablonski.md#transitions) |
| `jablonski.simulation` | `piecewise`, `step_excitation`, `pulse_excitation`, `delta_excitation`, `spectral_time_resolved_emission`, `time_resolved_emission`, `spectral_steady_state_emission`, `steady_state_emission`, `emission_spectra`, `widened_emission_spectra`, `excitation_emission_matrix`, `excitation_spectra`; *(newer)* `spectral_time_resolved`, `time_resolved`, `spectral_steady_state`, `steady_state`, `spectra`, `widened_spectra`, `quantum_yield`, `spectral_quantum_yield` | [jablonski.md](jablonski.md#simulation-workflows) |
| `jablonski.sweeps` | `sweep_emission_spectra`, `sweep_spectral_steady_state_emission`; *(newer)* `sweep_spectra`, `sweep_spectral_steady_state`, `sweep_quantum_yield` | [jablonski.md](jablonski.md#sweeps) |
| `jablonski.fits` *(newer)* | `fit_spectral_time_resolved`, `make_time_resolved_target`, `fit_spectra`, `make_spectra_target`, `fit_spectral_time_resolved_emission`, `make_time_resolved_emission_target`, `fit_emission_spectra` | [jablonski.md](jablonski.md#fits) |
| `jablonski.util` | `SpectraKind`; 0.4.0: `emission_transitions`, `excitation_transitions`; *(newer)* `yield_transitions`, `lines_and_transform` | [jablonski.md](jablonski.md#plots-reports-and-helpers) |
| `jablonski.helpers` | `pump_from_laser`, `h`, `c` | same |
| `jablonski.plots` | `jablonski_diagram`, `graph_spectra`, `model_report`, `notebook_report` (newer than the PyPI release) | same |
| `jablonski.rebop` | `RebopSimulator`, `rebop_piecewise`; *(newer)* `rebop_spectral_time_resolved`, `rebop_time_resolved`, `rebop_spectral_time_resolved_emission`, `rebop_time_resolved_emission` | [jablonski.md](jablonski.md#stochastic-runs) |

## Internal helpers (don't use)

These are importable but are implementation details, are dead code, or exist only to
support the functions above: `jablonski.simulation.lines_to_energies`,
`jablonski.util.TYPE_MAP` / `REVERSE_TYPE_MAP`, `jablonski.fits.Time` (a re-exported type
alias), `poincare.analysis.fits.UnitsHandler` / `parse_p0`,
`jablonski.rebop.rebop.distribute_points`, `jablonski.plots.plots.get_column`,
`sort_by_multiplicity`, `jablonski_diagram_section`, `jablonski_diagram_markdown`, `color_code_etu`, `jablonski.util.convert`
(dead code: it references undefined names), `simbio.core.first_system_parent`,
`is_instance_or_subclass`, `simbio.io.sbml.substitute_by_name.call_substitute_by_name` /
`value_substitute_by_name`, `poincare.compile.*` (compiler internals),
`poincare.simulator.rescale` / `get_scale` / `Problem`, the `poincare.printing.latex`
formatting helpers not listed above, and anything whose name starts with `_`.

## Not available in these versions

Don't look for these in poincare 1.2.0 / simbio 1.2.0 / jablonski 0.4.0. Use the documented
alternative instead. The third column says where newer versions (`main`, not on PyPI yet)
add them.

| Missing in the releases | Use instead | Newer versions |
| --- | --- | --- |
| A quantum-yield function in jablonski | The transform recipe in [jablonski.md](jablonski.md#quantum-yields) | `quantum_yield`, `spectral_quantum_yield`, `sweep_quantum_yield` |
| Absorption spectra / `kind="absorption"` in jablonski | `Absorption.absorption.rate_law` as a transform | `kind="absorption"` and lists of kinds |
| `jablonski.fits` | `poincare.analysis.fit_result` with jablonski transforms | `jablonski.fits` |
| A constant ground state in jablonski | A state with a large population, or a `Parameter` in a custom transition | `ConstantGroundState` |
| A `Fitter` class, `fit_steady_state`, fit covariances | `fit_result` (best values only) | `Fitter`, `fit_steady_state`, `FitResult.pcov` |
| `poincare.strip_units` | Build the model without units, or dequantify results | `poincare.strip_units` |
| `n_runs` argument on rebop solvers | A loop over seeds + `xr.concat(...).mean("run")` | `n_runs=` on `RebopSimulator.solve` and the jablonski rebop functions |
| `RebopSimulator.with_transform` | Compute derived outputs from the result | `with_transform` |
| A `Parameter` as a reactant (constant species) | Fold the constant into the rate (`rate=k * G_value`) | `Parameter` reactants |
| Generic jablonski names (`time_resolved`, `steady_state`, `spectra`, …) | The `*_emission` functions (kept as wrappers in newer versions) | Generic names |
