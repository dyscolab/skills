# Changelog

## Unreleased

- After declaring a model, show a model report as proof that it works. In notebooks use
  `poincare.printing.notebook_report` (needs poincare newer than 1.2.0); in scripts use
  `model_report`.
- Document the report crash for compartments with a constant `Volume`, and its workaround.

## 1.0.0

- `dyscolab-modeling` skill for poincare 1.2.x, simbio 1.2.x and jablonski 0.4.x:
  - `SKILL.md` with library selection, core pattern, common pitfalls, scope rules and file
    layout guidance.
  - References for poincare, analysis, units, simbio, jablonski, workflows and the public
    API inventory.
  - Seven tested examples with physics checks.
- Claude Code marketplace manifest (`dyscolab@dyscolab`).
