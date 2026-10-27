# Dyscolab agent skills

[Agent Skills](https://agentskills.io) that teach coding agents how to model systems with
the Dyscolab libraries:

| Skill | What it covers |
| --- | --- |
| [`dyscolab-modeling`](skills/dyscolab-modeling/SKILL.md) | Declaring, simulating and analysing models with [poincare](https://github.com/dyscolab/poincare) (ODEs), [simbio](https://github.com/dyscolab/simbio) (reaction networks, compartments, SBML) and [jablonski](https://github.com/dyscolab/jablonski) (photophysics) |

The skill on `main` documents **poincare 1.2.x, simbio 1.2.x and jablonski 0.4.x**.

## Install

The skills use the open `SKILL.md` format, so they work with any agent that supports
Agent Skills.

**Any agent (Codex, Cursor, GitHub Copilot, Gemini CLI, Claude Code, Windsurf, Goose, …)**
with the [skills CLI](https://skills.sh):

```sh
npx skills add dyscolab/skills
```

**Claude Code**, as a plugin marketplace:

```sh
claude plugin marketplace add dyscolab/skills
claude plugin install dyscolab@dyscolab
```

**Manually:** copy `skills/dyscolab-modeling/` into your agent's skills directory (for
example `.agents/skills/`, `.claude/skills/` or `~/.codex/skills/`).

The skill expects the libraries in the Python environment the agent uses:

```sh
pip install poincare "simbio[io]" jablonski rebop
```

## Repository layout

```
skills/<name>/SKILL.md         # the skill (open Agent Skills format)
skills/<name>/references/      # detailed docs, loaded on demand
skills/<name>/examples/        # runnable scripts with physics checks
.claude-plugin/marketplace.json  # Claude Code marketplace manifest (points at skills/)
tests/                         # runs every example and validates the metadata
```

## Development

```sh
pixi run test              # Python 3.14, pinned library versions
pixi run -e py312 test     # also py313
```

`main` only changes at releases. Unreleased work, including documentation for library
features that are not on PyPI yet, goes to `dev`. See [AGENTS.md](AGENTS.md).

## License

MIT
