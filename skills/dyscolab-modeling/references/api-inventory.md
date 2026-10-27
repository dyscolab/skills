# Public API inventory (poincare 1.2.0, simbio 1.2.0, jablonski 0.4.0)

Use this to check that a name exists in these versions before you write code with it. When
the installed version differs, check the installed source instead
(`python -c "import jablonski.simulation as m; print(dir(m))"`).

Single-file modules (for example `jablonski.transitions` or `jablonski.simulation`) are part
of the public API just like package `__init__` exports.

## poincare

| Module | Names | Reference |
| --- | --- | --- |
| `poincare` | `System`, `Variable`, `Derivative`, `Parameter`, `Constant`, `Independent`, `initial`, `assign`, `Simulator`, `SteadyState`, `Oscillations`, `model_report` | [poincare.md](poincare.md) |
| `poincare.solvers` | `LSODA`, `RK23`, `RK45`, `DOP853`, `Radau`, `BDF` (and the `Solver` protocol) | [poincare.md](poincare.md#simulator) |
| `poincare.simulator` | `Simulator`, plus the `Components` type alias (Constant \| Parameter \| Variable \| Derivative) | [poincare.md](poincare.md#simulator) |
| `poincare.analysis` | `SteadyState`, `Oscillations`, `Sweeper`, `fit_result` | [analysis.md](analysis.md) |
| `poincare.analysis.fits` | `fit_result`, `make_target` | [analysis.md](analysis.md#fitting-parameters-to-data) |
| `poincare.reactions` | `Reactant`, `reaction_initial`, `RateLaw`, `MassAction`, `AbsoluteRateLaw` | [simbio.md](simbio.md#reactions) |
| `poincare.reactions.rebop` | `RebopSimulator` | [analysis.md](analysis.md#stochastic-simulation-rebop) |
| `poincare.printing.latex` | `model_report`, `latex_equations`, `parameter_table`, `variable_table`, `ToLatex` | [poincare.md](poincare.md#reports-and-introspection) |
| `poincare.helpers` | `get_from`, `to_values` | [poincare.md](poincare.md#reports-and-introspection) |

## simbio

| Module | Names | Reference |
| --- | --- | --- |
| `simbio` | re-exports from poincare (`System`, `Variable`, `Parameter`, `Constant`, `Independent`, `Simulator`, `initial`, `assign`, `Reactant`, `reaction_initial`, `RateLaw`, `MassAction`, `AbsoluteRateLaw`) plus `Compartment`, `Species`, `Volume`, `amount`, `concentration`, `volume`, `reaction_amount`, `reaction_concentration`, `model_report` | [simbio.md](simbio.md) |
| `simbio.reactions` (`.single`, `.compound`, `.enzymatic`) | `Creation`, `AutoCreation`, `Destruction`, `Conversion`, `Synthesis`, `Dissociation`, `ReversibleSynthesis`, `Equilibration`, `CatalyzeConvert`, `MichaelisMenten`, `MichaelisMentenEqApprox`, `MichaelisMentenQuasiSSAprox` | [simbio.md](simbio.md#reaction-motifs) |
| `simbio.io.sbml` | `load`, `loads` (Python ≥ 3.14 with 1.2.0) | [simbio.md](simbio.md#sbml-biomodels-and-mathml) |
| `simbio.io.biomodels` | `load` | same |
| `simbio.io.mathML` | `to_mathML`, `mathMLImporter` | same |
| `simbio.io.sbml.substitute_by_name` | `substitute_by_name` | same |
| `simbio.io.graph.networkx` | `graph`, `to_Variable_graph`, `to_reaction_graph` | [simbio.md](simbio.md#graphs-reports-stochastic-runs) |
| `simbio.rebop` | `RebopSimulator` | [analysis.md](analysis.md#stochastic-simulation-rebop) |

## jablonski

| Module | Names | Reference |
| --- | --- | --- |
| `jablonski` | `SpectroscopicSystem`, `SingletState`, `TripletState`, `initial`, `Parameter`, `assign`, `Simulator`, `pump_from_laser`, submodules `transitions`, `simulation`, `sweeps`, `util` | [jablonski.md](jablonski.md) |
| `jablonski.states` | `SpinState`, `SingletState`, `TripletState`, `initial`, `SpectroscopicSystem` | [jablonski.md](jablonski.md#states) |
| `jablonski.transitions` | `Absorption`, `TripletTripletAbsorption`, `Fluorescence`, `Phosphorescence`, `InternalConversion`, `VibrationalRelaxation`, `IntersystemCrossing`, `ReverseIntersystemCrossing`, `EnergyTransferUpconversion`, `EnergyTransferUpconversion4`, `check_all` | [jablonski.md](jablonski.md#transitions) |
| `jablonski.simulation` | `piecewise`, `step_excitation`, `pulse_excitation`, `delta_excitation`, `spectral_time_resolved_emission`, `time_resolved_emission`, `spectral_steady_state_emission`, `steady_state_emission`, `emission_spectra`, `widened_emission_spectra`, `excitation_emission_matrix`, `excitation_spectra` | [jablonski.md](jablonski.md#simulation-workflows) |
| `jablonski.sweeps` | `sweep_emission_spectra`, `sweep_spectral_steady_state_emission` | [jablonski.md](jablonski.md#sweeps) |
| `jablonski.util` | `emission_transitions`, `excitation_transitions`, `SpectraKind` | [jablonski.md](jablonski.md#plots-reports-and-helpers) |
| `jablonski.helpers` | `pump_from_laser`, `h`, `c` | same |
| `jablonski.plots` | `jablonski_diagram`, `graph_spectra`, `model_report` | same |
| `jablonski.rebop` | `RebopSimulator`, `rebop_piecewise` | [jablonski.md](jablonski.md#stochastic-runs) |

## Internal helpers (don't use)

These are importable but are implementation details, are dead code, or exist only to
support the functions above: `jablonski.simulation.lines_to_energies`,
`jablonski.rebop.rebop.distribute_points`, `jablonski.plots.plots.get_column`,
`sort_by_multiplicity`, `jablonski_diagram_section`, `color_code_etu`, `jablonski.util.convert`
(dead code: it references undefined names), `simbio.core.first_system_parent`,
`is_instance_or_subclass`, `simbio.io.sbml.substitute_by_name.call_substitute_by_name` /
`value_substitute_by_name`, `poincare.compile.*` (compiler internals),
`poincare.simulator.rescale` / `get_scale` / `Problem`, the `poincare.printing.latex`
formatting helpers not listed above, and anything whose name starts with `_`.

## Not available in these versions

Don't look for these in poincare 1.2.0 / simbio 1.2.0 / jablonski 0.4.0. Use the documented
alternative instead:

| Missing | Use instead |
| --- | --- |
| A quantum-yield function in jablonski | The transform recipe in [jablonski.md](jablonski.md#quantum-yields) |
| Absorption spectra / `kind="absorption"` in jablonski | `Absorption.absorption.rate_law` as a transform |
| `jablonski.fits` | `poincare.analysis.fit_result` with jablonski transforms |
| A `Fitter` class, `fit_steady_state`, fit covariances | `fit_result` (best values only) |
| `poincare.strip_units` | Build the model without units, or dequantify results |
| `n_runs` argument on rebop solvers | A loop over seeds + `xr.concat(...).mean("run")` |
| Generic jablonski names (`time_resolved`, `steady_state`, `spectra`, …) | The `*_emission` functions |
