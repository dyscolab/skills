# AGENTS.md: dyscolab/skills

Instructions for coding agents maintaining this repository. The skills here are *for*
agents that use poincare, simbio and jablonski. This file is for agents that edit the skills.

## What this is

- **The skill content is not written here.** The `dyscolab-modeling` skill is bundled
  with the libraries: poincare, simbio and jablonski each keep their part in
  `skill/share/agent-skills/dyscolab-modeling/` and install it to
  `<environment>/share/agent-skills/` (where `pixi skills` finds it). poincare holds
  `SKILL.md`, `poincare.skill` merges the parts. Edit the content in the library
  repositories, in the same PR as the API change it documents.
- **This repository distributes a separate copy** for agents whose users install skills
  without the libraries (skills CLI, Claude Code plugin marketplace, manual copy).
  `skills/dyscolab-modeling/` is **generated** by `scripts/build_skill.py` from the
  libraries installed at the versions pinned in `pixi.toml`. Never edit it by hand.
- The build replaces the "Versions and environment" section of SKILL.md, between
  `<!-- dyscolab-skill:versions-section:start -->` and `...:end -->`, with
  `templates/versions-section.md` (`$poincare`, `$simbio`, `$jablonski` and
  `$skill_version` are filled in), and sets the frontmatter `compatibility` and `metadata`
  (`version`, `libraries`). The bundled section tells agents how to update a bundled
  copy. The template tells them how to move from this copy to the bundled one.
- Keep the content agent-neutral: no tool names, slash commands or features of a specific
  agent.
- `.claude-plugin/marketplace.json` is the Claude Code adapter. It lists the skill folders,
  and the skills CLI (skills.sh) also reads it.

## Branches and releases

- **`main` is what users install** (all installers take the default branch head). Commit to
  it only to release.
- **`dev`** collects changes to the build script, template, tests and docs.
- **Release** (after a poincare, simbio or jablonski release):
  1. Update the pinned versions in `pixi.toml` to the new releases.
  2. `pixi run build`, then `pixi run test` (and `-e py312`, `-e py313`).
  3. Bump `version` in `.claude-plugin/marketplace.json` (`metadata.version` and the
     plugin `version`), and build again so that SKILL.md has it.
  4. Update CHANGELOG.md with the library versions.
  5. Merge `dev` → `main` and tag `v<version>`.

## Accuracy rules

- Content errors are fixed in the library that ships the file, then the skill is rebuilt
  here after the library's release.
- Each example ends with a physics assertion (analytic solution, conservation, scaling
  law) with explicit tolerances. Each library runs its own examples in its test suite.
  `pixi run test` here runs them again against the pinned releases, on Python 3.12–3.14.
- Document known library bugs as user-facing workarounds. Report them upstream rather than
  hiding them.
- `references/api-inventory.md` (poincare), `simbio-api.md` and `jablonski-api.md` list
  every public name. Single-file modules count as public namespaces, and internal helpers
  are listed as such.

## Commands

```sh
pixi run build                # regenerate skills/dyscolab-modeling from the pinned libraries
pixi run test                 # default env (Python 3.14)
pixi run -e py312 test        # also py313
claude plugin validate .      # marketplace manifest (optional, needs Claude Code)
```

The build needs a poincare release that ships `poincare.skill` (newer than 1.2.0). Until
then, build and test from the u2602 workspace, where `pixi run test-skills` builds the
skill from the development sources of all libraries into `.build/` and runs these tests
on it.

## Commits

Use conventional commits (`feat(build): ...`, `docs: ...`, `test: ...`).
