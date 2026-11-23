"""Build the separate dyscolab-modeling skill from the skill bundled with the libraries.

poincare, simbio and jablonski each ship their part of the skill (see `poincare.skill`).
This script merges the parts of the installed libraries, replaces the "Versions and
environment" section of SKILL.md with templates/versions-section.md, and sets the
frontmatter for a separate distribution. Run it in an environment with all three
libraries installed (`pixi run build`), at the versions the skill should document.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from string import Template

from poincare import skill

ROOT = Path(__file__).parents[1]
TEMPLATE = ROOT / "templates" / "versions-section.md"
MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"


def skill_version() -> str:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    (version,) = {plugin["version"] for plugin in manifest["plugins"]}
    return version


def set_frontmatter(text: str, fields: dict[str, str], metadata: dict[str, str]) -> str:
    """Set top-level ``fields`` and the ``metadata`` mapping of the YAML frontmatter."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if match is None:
        raise ValueError("SKILL.md must start with YAML frontmatter")
    lines = match.group(1).splitlines()
    keep: list[str] = []
    in_metadata = False
    for line in lines:
        if line.startswith("metadata:"):
            in_metadata = True
            continue
        if in_metadata and line.startswith((" ", "\t")):
            continue
        in_metadata = False
        if line.split(":", 1)[0] not in fields:
            keep.append(line)
    keep += [f"{key}: {value}" for key, value in fields.items()]
    keep.append("metadata:")
    keep += [f"  {key}: {json.dumps(value)}" for key, value in metadata.items()]
    return "---\n" + "\n".join(keep) + "\n---\n" + text[match.end() :]


def build(out: Path) -> dict[str, str]:
    parts = skill.find_parts()
    missing = [part.describe() for part in parts if not part.files]
    if missing:
        sys.exit(
            "The skill needs all three libraries with their skill files: " + ", ".join(missing)
        )

    versions = {part.package: part.version for part in parts}
    files = skill.assemble(parts, stamp=False)

    text = files["SKILL.md"].decode("utf-8")
    section = Template(TEMPLATE.read_text(encoding="utf-8")).substitute(
        skill_version=skill_version(), **versions
    )
    text = skill.replace_block(text, skill.SECTION_START, skill.SECTION_END, section)
    text = set_frontmatter(
        text,
        {
            "compatibility": "Python >= 3.12. Documents poincare {poincare}, simbio {simbio} "
            "and jablonski {jablonski}.".format(**versions)
        },
        {
            "version": skill_version(),
            "libraries": ", ".join(f"{name}=={version}" for name, version in versions.items()),
        },
    )
    files["SKILL.md"] = text.encode("utf-8")

    if out.exists():
        shutil.rmtree(out)
    for relative, content in files.items():
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return versions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "skills" / skill.SKILL_NAME,
        help="output folder (default: skills/dyscolab-modeling)",
    )
    args = parser.parse_args()
    versions = build(args.out)
    print(f"Built {args.out} from " + ", ".join(f"{n} {v}" for n, v in versions.items()))


if __name__ == "__main__":
    main()
