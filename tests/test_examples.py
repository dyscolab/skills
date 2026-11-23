"""Run every example of the built skill.

The examples come from the libraries (see scripts/build_skill.py), so they match the
installed versions and need no version-specific skips.
"""

import importlib.util
import os
from pathlib import Path
from runpy import run_path

import matplotlib
import pytest

matplotlib.use("Agg")

# DYSCOLAB_SKILLS_DIR: a folder of built skills (the workspace's test-skills task).
SKILLS = Path(os.environ.get("DYSCOLAB_SKILLS_DIR", Path(__file__).parents[1] / "skills"))
examples = sorted(SKILLS.glob("*/examples/*.py"))
NEEDS = {"simbio_sbml.py": "libsbml", "simbio_stochastic.py": "rebop"}


@pytest.mark.filterwarnings("ignore")
@pytest.mark.parametrize("example", examples, ids=[p.stem for p in examples])
def test_example(example: Path):
    if (module := NEEDS.get(example.name)) and importlib.util.find_spec(module) is None:
        pytest.skip(f"needs {module}")
    run_path(str(example), run_name="test")
