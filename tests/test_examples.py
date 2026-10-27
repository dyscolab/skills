import sys
from pathlib import Path
from runpy import run_path

import matplotlib
import pytest

matplotlib.use("Agg")

EXAMPLES = Path(__file__).parents[1] / "skills" / "dyscolab-modeling" / "examples"
examples = sorted(EXAMPLES.glob("*.py"))

# simbio 1.2.0's SBML/MathML import needs Python >= 3.14 (NameError on older versions).
needs_py314 = {"simbio_sbml.py"}


@pytest.mark.filterwarnings("ignore")
@pytest.mark.parametrize("example", examples, ids=[p.stem for p in examples])
def test_example(example: Path):
    if example.name in needs_py314 and sys.version_info < (3, 14):
        pytest.skip("simbio 1.2.0 SBML import requires Python >= 3.14")
    run_path(str(example), run_name="test")
