# Public API inventory: simbio (1.2.0 and newer)

Use this to check that a name exists before you write code with it. When the installed
version differs, check the installed source instead
(`python -c "import simbio.reactions as m; print(dir(m))"`). The poincare inventory is in
[api-inventory.md](api-inventory.md).

Names marked *(newer)* exist only after simbio 1.2.0.

## simbio

| Module | Names | Reference |
| --- | --- | --- |
| `simbio` | re-exports from poincare (`System`, `Variable`, `Parameter`, `Constant`, `Independent`, `Simulator`, `initial`, `assign`, `Reactant`, `reaction_initial`, `RateLaw`, `MassAction`, `AbsoluteRateLaw`) plus `Compartment`, `Species`, `Volume`, `amount`, `concentration`, `volume`, `reaction_amount`, `reaction_concentration`, `model_report`, `notebook_report` *(newer)* | [simbio.md](simbio.md) |
| `simbio.reactions` (`.single`, `.compound`, `.enzymatic`) | `Creation`, `AutoCreation`, `Destruction`, `Conversion`, `Synthesis`, `Dissociation`, `ReversibleSynthesis`, `Equilibration`, `CatalyzeConvert`, `MichaelisMenten`, `MichaelisMentenEqApprox`, `MichaelisMentenQuasiSSAprox` | [simbio.md](simbio.md#reaction-motifs) |
| `simbio.io.sbml` | `load`, `loads` (Python ≥ 3.14 with 1.2.0) | [simbio.md](simbio.md#sbml-biomodels-and-mathml) |
| `simbio.io.biomodels` | `load` | same |
| `simbio.io.mathML` | `to_mathML`, `mathMLImporter` | same |
| `simbio.io.sbml.substitute_by_name` (newer: `simbio.io.substitute_by_name`) | `substitute_by_name` | same |
| `simbio.latex` | `latex_reactions` (*(newer)* `format=`), `model_report`, `notebook_report` *(newer)* | [simbio.md](simbio.md#graphs-reports-stochastic-runs) |
| `simbio.io.graph.networkx` | `graph`, `to_Variable_graph`, `to_reaction_graph` | [simbio.md](simbio.md#graphs-reports-stochastic-runs) |
| `simbio.rebop` | `RebopSimulator` | [analysis.md](analysis.md#stochastic-simulation-rebop) |
| `simbio.skill` *(newer)* | `install`, `check`: the same as `poincare.skill` | [SKILL.md](../SKILL.md#versions-and-environment) |

## Internal helpers (don't use)

`simbio.core.first_system_parent`, `is_instance_or_subclass`,
`simbio.io.sbml.substitute_by_name.call_substitute_by_name` / `value_substitute_by_name`,
and anything whose name starts with `_`.
