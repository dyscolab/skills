# AGENTS.md: dyscolab/skills

Instructions for coding agents maintaining this repository. The skills here are *for*
agents that use poincare, simbio and jablonski. This file is for agents that edit the skills.

## What this is

- `skills/<name>/` holds one skill in the open Agent Skills format: `SKILL.md` plus
  `references/` and `examples/`. Keep its content agent-neutral: no tool names, slash
  commands or features of a specific agent.
- `.claude-plugin/marketplace.json` is the Claude Code adapter. It lists the skill folders,
  and the skills CLI (skills.sh) also reads it.

## Branches and releases

- **`main` is what users install** (all installers take the default branch head). Commit to
  it only to release.
- **`dev` collects unreleased work.** This includes documentation for library features that
  are on poincare/simbio/jablonski `main` but not yet on PyPI.
- **Release:**
  1. Merge `dev` → `main`.
  2. Update the pinned versions in `pixi.toml` and the `compatibility`/`metadata` in
     `SKILL.md`.
  3. Bump `version` in `SKILL.md` metadata and in `.claude-plugin/marketplace.json`
     (`metadata.version` and the plugin `version`).
  4. Update CHANGELOG.md.
  5. Tag `v<version>`.

## Accuracy rules

- **Every API statement must hold for the pinned library versions in `pixi.toml`.** Check
  it in that environment (`pixi run python ...`) or in the installed source, not in a
  development checkout.
- Each example ends with a physics assertion (analytic solution, conservation, scaling
  law) with explicit tolerances, and runs in `pixi run test` on Python 3.12–3.14. Mark
  version-specific skips in `tests/test_examples.py` with the reason.
- Document known library bugs as user-facing workarounds. Report them upstream rather than
  hiding them.
- `references/api-inventory.md` lists every public name. Single-file modules count as
  public namespaces, and internal helpers are listed as such.

## Commands

```sh
pixi run test                 # default env (Python 3.14)
pixi run -e py312 test        # also py313
claude plugin validate .      # marketplace manifest (optional, needs Claude Code)
```

Inside the u2602 workspace, `pixi run test-skills` runs the examples against the development
sources of all libraries. It is meant for the `dev` branch.

## Commits

Use conventional commits (`feat(dyscolab-modeling): ...`, `docs: ...`, `test: ...`).
