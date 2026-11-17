import inspect
import sys
from pathlib import Path
from runpy import run_path

import matplotlib
import pytest
from poincare import Simulator

matplotlib.use("Agg")

EXAMPLES = Path(__file__).parents[1] / "skills" / "dyscolab-modeling" / "examples"
examples = sorted(EXAMPLES.glob("*.py"))

# simbio 1.2.0's SBML/MathML import needs Python >= 3.14 (NameError on older versions).
needs_py314 = {"simbio_sbml.py"}

# Simulator.with_times / RebopSimulator.with_times are newer than poincare 1.2.0.
needs_with_times = {
    "poincare_oscillator.py",
    "simbio_compartments.py",
    "simbio_sbml.py",
    "simbio_stochastic.py",
}

# save_at=None in jablonski's simulation functions is newer than jablonski 0.4.0.
needs_jablonski_times = {"jablonski_quantum_yield.py", "jablonski_upconversion.py"}


def _jablonski_takes_times_from_simulator() -> bool:
    from jablonski.simulation import piecewise

    return inspect.signature(piecewise).parameters["save_at"].default is None


@pytest.mark.filterwarnings("ignore")
@pytest.mark.parametrize("example", examples, ids=[p.stem for p in examples])
def test_example(example: Path):
    if example.name in needs_py314 and sys.version_info < (3, 14):
        pytest.skip("simbio 1.2.0 SBML import requires Python >= 3.14")
    if example.name in needs_with_times and not hasattr(Simulator, "with_times"):
        pytest.skip("with_times requires poincare newer than 1.2.0")
    if example.name in needs_jablonski_times and not _jablonski_takes_times_from_simulator():
        pytest.skip("times from with_times require jablonski newer than 0.4.0")
    run_path(str(example), run_name="test")
