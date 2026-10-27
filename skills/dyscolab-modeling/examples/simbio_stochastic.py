"""Stochastic (Gillespie) simulation of a reaction network with rebop.

A -> 0 with rate k: the mean of many stochastic runs follows the ODE solution
N0 exp(-k t). Requires `pip install rebop`.
"""

import numpy as np
import xarray as xr

from simbio import MassAction, Simulator, System, Variable, initial
from simbio.rebop import RebopSimulator


class Decay(System):
    A: Variable = initial(default=500)  # copy numbers: integers, no units
    degradation = MassAction(reactants=[A], products=[], rate=0.5)


rsim = RebopSimulator(Decay)
# n_points equally spaced samples after t = 0, so n_points + 1 time points.
runs = xr.concat(
    [rsim.solve(upto_t=4, n_points=8, rng=seed) for seed in range(40)], dim="run"
)
mean = runs["A"].mean("run")
t = mean["time"].values
np.testing.assert_allclose(mean.values, 500 * np.exp(-0.5 * t), rtol=0.05)

# The same model runs deterministically with the ODE simulator.
ode = Simulator(Decay).solve(save_at=t)
np.testing.assert_allclose(ode["A"].values, 500 * np.exp(-0.5 * t), rtol=1e-2)
