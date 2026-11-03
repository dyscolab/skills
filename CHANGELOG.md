# Changelog

## Unreleased

- After declaring a model, show a model report as proof that it works. In notebooks use
  `poincare.printing.notebook_report` (needs poincare newer than 1.2.0); in scripts use
  `model_report`.
- Document `notebook_report`'s `transform`, `descriptions`, `replace_algebraics`, `sections`
  and `level` arguments, and the simbio (`simbio.notebook_report`, with reactions) and
  jablonski (`jablonski.plots.notebook_report`, with the Jablonski diagram) versions. Use
  the one matching the model's library.
- Document the report crash for compartments with a constant `Volume`, and its workaround.

## 1.0.0

- `dyscolab-modeling` skill for poincare 1.2.x, simbio 1.2.x and jablonski 0.4.x:
  - `SKILL.md` with library selection, core pattern, common pitfalls, scope rules and file
    layout guidance.
  - References for poincare, analysis, units, simbio, jablonski, workflows and the public
    API inventory.
  - Seven tested examples with physics checks.
- Claude Code marketplace manifest (`dyscolab@dyscolab`).
