# Changelog

## Unreleased

- After declaring a model, show a model report as proof that it works. In notebooks use
  `poincare.printing.notebook_report` (needs poincare newer than 1.2.0); in scripts use
  `model_report`.
- Document `notebook_report`'s `transform`, `descriptions`, `replace_algebraics`, `sections`
  and `level` arguments, and the simbio (`simbio.notebook_report`, with reactions) and
  jablonski (`jablonski.plots.notebook_report`, with the Jablonski diagram) versions. Use
  the one matching the model's library.
- Document the report crash for compartments with a constant `Volume`, and its workaround
  (fixed in newer poincare).
- Fix the jablonski examples for jablonski `main` while keeping them working on 0.4.0:
  `jablonski_quantum_yield.py` reads the total `emission` instead of the renamed per-line
  output (`line_<transition>` → `emission_<transition>`), and `jablonski_upconversion.py`
  imports the four-state ETU under either name (`EnergyTransferUpconversion4` →
  `EnergyTransferUpconversion`).
- Document unreleased jablonski changes, each marked "newer than 0.4.0": generic simulation
  names, `kind="absorption"` and lists of kinds, `quantum_yield`, `spectral_quantum_yield`
  and `sweep_quantum_yield`, `jablonski.fits`, `ConstantGroundState`, rebop `n_runs` and
  spectral functions, the ETU rename, the `t = 0` event and spectra-unit fixes, and that
  custom radiative transitions can no longer subclass `Fluorescence`. `check_all` is broken
  in 0.4.0 and fixed on `main`.
- Document unreleased poincare changes, each marked "newer than 1.2.0": the reworked fits
  (`FitResult.pcov`, `sigma`, `Fitter`, `fit_steady_state`), `strip_units`, `Parameter`
  reactants as constant species, rebop `n_runs`/`with_transform`, removal of
  `Simulator(solver=)`, missing values reported at `solve`, and the new `t_span` default.
  Document that integration starts at `save_at[0]` when no `t_span` is given.
- Document unreleased simbio changes: SBML import on Python < 3.14, `latex_reactions(format=)`,
  and the new location of `substitute_by_name`.

## 1.0.0

- `dyscolab-modeling` skill for poincare 1.2.x, simbio 1.2.x and jablonski 0.4.x:
  - `SKILL.md` with library selection, core pattern, common pitfalls, scope rules and file
    layout guidance.
  - References for poincare, analysis, units, simbio, jablonski, workflows and the public
    API inventory.
  - Seven tested examples with physics checks.
- Claude Code marketplace manifest (`dyscolab@dyscolab`).
