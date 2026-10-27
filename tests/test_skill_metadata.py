"""Check skills against the Agent Skills spec and the marketplace manifest."""

import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]
SKILLS = sorted(p.parent for p in (ROOT / "skills").glob("*/SKILL.md"))


def frontmatter(skill: Path) -> dict:
    text = (skill / "SKILL.md").read_text()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    return yaml.safe_load(match.group(1))


@pytest.mark.parametrize("skill", SKILLS, ids=[p.name for p in SKILLS])
def test_frontmatter(skill: Path):
    fm = frontmatter(skill)
    assert fm["name"] == skill.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm["name"]) and len(fm["name"]) <= 64
    assert 0 < len(fm["description"]) <= 1024
    assert len(fm.get("compatibility", "")) <= 500
    assert all(isinstance(v, str) for v in fm.get("metadata", {}).values())
    assert set(fm) <= {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


@pytest.mark.parametrize("skill", SKILLS, ids=[p.name for p in SKILLS])
def test_relative_links_exist(skill: Path):
    for md in skill.rglob("*.md"):
        for target in re.findall(r"\]\(([^)#:]+)(?:#[^)]*)?\)", md.read_text()):
            assert (md.parent / target).exists(), f"{md.relative_to(ROOT)} links to missing {target}"


def test_marketplace_lists_every_skill():
    manifest = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    listed = {
        (ROOT / path).resolve() for plugin in manifest["plugins"] for path in plugin["skills"]
    }
    assert listed == {p.resolve() for p in SKILLS}
    versions = {plugin["version"] for plugin in manifest["plugins"]}
    for skill in SKILLS:
        assert frontmatter(skill)["metadata"]["version"] in versions
