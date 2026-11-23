## Versions and environment

This copy of the skill is distributed **separately from the libraries**
([github.com/dyscolab/skills](https://github.com/dyscolab/skills), skill version
$skill_version). It documents these releases:

- poincare $poincare
- simbio $simbio
- jablonski $jablonski

**Check the installed versions** in the environment you work in before writing code, with
that environment's Python:

```python
from importlib.metadata import version
print({p: version(p) for p in ("poincare", "simbio", "jablonski")})
```

If they differ from the list above:

- **If `python -m poincare.skill` exists** (poincare releases after 1.2.0), the
  libraries bundle this skill at the installed versions. Use that one instead:
  `python -m poincare.skill install --dest <agent skills folder>` copies it (in pixi
  projects, `pixi skills manage` can link it instead). Then remove this copy with the
  tool that installed it (the skills CLI or the Claude Code plugin manager), so that
  only one `dyscolab-modeling` skill is left.
- **Otherwise**, update this copy with the tool that installed it, or read the installed
  sources where they disagree with this skill.

**Installing the libraries:** poincare and jablonski are published on PyPI and
conda-forge, simbio and rebop (stochastic runs) on PyPI. simbio's SBML import needs its
`io` extra (`simbio[io]`). Install them with the tool that manages the project's
environment (pixi, conda/mamba, uv, pip, …), and don't mix tools in one environment.

Notes marked "newer than" a release describe what changed after that release. If the
installed source disagrees with this skill, the installed source wins.
