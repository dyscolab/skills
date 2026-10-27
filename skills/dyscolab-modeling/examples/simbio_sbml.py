"""Import an SBML model with simbio and simulate it with poincare.

data/decay.xml is X -> 0 with k = 0.5 and X(0) = 10, checked against
X(t) = 10 exp(-0.5 t).

Requires the `io` extra (`pip install "simbio[io]"`). simbio 1.2.0's SBML import
only works on Python >= 3.14; older Pythons fail at import with
`NameError: name 'types' is not defined`.
"""

from pathlib import Path

import numpy as np

from poincare import solvers
from simbio import Simulator
from simbio.io import sbml

path = Path(__file__).parent / "data" / "decay.xml"
Decay = sbml.load(path)  # a poincare System class; pass name=... if the SBML model has none

# Components are class attributes named after their SBML ids.
print(Decay)  # summary table of variables, parameters and equations
assert {"X", "k", "deg"} <= set(vars(Decay))

sim = Simulator(Decay).with_solver(solvers.LSODA(rtol=1e-9, atol=1e-12))
t = np.linspace(0, 6, 31)
result = sim.solve(save_at=t)
np.testing.assert_allclose(result["X"].values, 10 * np.exp(-0.5 * t), rtol=1e-6)

# Parameters and initial values are changed like in any other model.
faster = sim.with_values({Decay.k: 1.0, Decay.X: 5}).solve(save_at=t)
np.testing.assert_allclose(faster["X"].values, 5 * np.exp(-1.0 * t), rtol=1e-6)

# The same model from a string; `name` is required when the SBML has no name.
Decay2 = sbml.loads(path.read_text(), name="DecayFromString")
assert Decay2.__name__ == "DecayFromString"
