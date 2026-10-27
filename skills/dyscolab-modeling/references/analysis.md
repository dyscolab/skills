# Analysis with poincare 1.2: steady states, sweeps, oscillations, fits, stochastic runs

All of these take a `Simulator` (configure values, solver and transforms on it first).
For simbio and jablonski models, import them from `poincare`, because simbio and jablonski
do not re-export them.

## Contents

- [Steady states](#steady-states)
- [Parameter sweeps](#parameter-sweeps)
- [Bistability](#bistability)
- [Oscillations and limit cycles](#oscillations-and-limit-cycles)
- [Fitting parameters to data](#fitting-parameters-to-data)
- [Stochastic simulation (rebop)](#stochastic-simulation-rebop)

## Steady states

```python
from poincare import SteadyState, Simulator, solvers

sim = Simulator(Model).with_solver(solvers.LSODA(rtol=1e-8, atol=1e-10))
ss = SteadyState().solve(sim.with_values({Model.k: 2}))   # or just solve(sim)
ss["x"].item(), ss["event"].item()                    # event == 0 → converged
```

- Pass parameter values through `sim.with_values(...)`. `SteadyState.solve` also accepts
  `values=` in 1.2.0, but newer poincare removes it, so the `with_values` form is the
  portable one.
- `SteadyState(condition=SmallDerivatives(), t_end=<float max>)` integrates until every
  derivative is small, then stops. The result has one time point plus an `event` column.
- **Accuracy follows the solver tolerances.** The default condition stops when
  `|dy/dt| < 10·atol` or `< 10·rtol·|y|`, so the default solver (rtol 1e-3) gives
  steady states that are only accurate to about 1 %. Use `with_solver(LSODA(rtol=1e-8, atol=...))`.
  Choose `atol` well below the smallest population or concentration you care about.
- Set `t_end` (in base units) to bound runs that might not converge. **In 1.2.0, a run
  that reaches `t_end` without converging raises an obscure
  `ValueError: could not broadcast input array ...`** instead of returning `event != 0`.
  This happens for oscillating or slowly drifting systems. Catch it, then simulate
  a time course or use `Oscillations`.
- A steady state from integration depends on the initial condition (multistability).
  Set the initial values with `with_values` to pick a branch.

## Parameter sweeps

**Default pattern: loop + `xr.concat`.** It works with units, transforms and any output.

```python
import xarray as xr

values = [0.5, 1, 2] * u.mM / u.s
sweep = xr.concat(
    [SteadyState().solve(sim.with_values({Model.p: v})).isel(time=-1) for v in values],
    dim="p",
).assign_coords(p=values.magnitude)
```

`isel(time=-1)` matters: without it, the runs (which stop at different times) are aligned
on `time` and padded with NaN. The same loop works for time courses
(`sim.with_values({...}).solve(save_at=...)`, concatenated on a new dimension) and for
2D sweeps (nest two loops, or concat a list of 1D sweeps).

Built-in helpers, which work only in simple cases in 1.2.0:

- `SteadyState().sweep(sim, variable=Model.p, values=[...])` returns the steady state of
  each state variable along a dimension named after the parameter.
  - It **fails when state variables carry units**.
  - It **fails when the simulator has a transform without `append=True`**.
  - It drops transform outputs.
  - Use the loop in those cases.
- `Sweeper(func).sweep(sim, parameter=Model.p, values=[...], save_at=...)` runs a full
  simulation per value and applies `func(dataset)`. Use it for derived scalars such as
  peak height or final value. If `func` returns a dict, each key becomes a variable.

## Bistability

```python
uad = SteadyState().sweep_up_and_down(sim, variable=Model.c, values=np.linspace(-3, 3, 30))
uad.sel(direction="up")["x"], uad.sel(direction="down")["x"]
SteadyState().bistability(sim, variable=Model.c, values=..., atol=0.1, rtol=0.01)  # bool per value
```

The up/down sweep seeds each run with the previous steady state, so hysteresis shows up as
different branches.

## Oscillations and limit cycles

```python
from poincare import Oscillations

res = Oscillations().sweep(
    sim, parameter=Model.w, values=np.linspace(1, 2, 20),
    T_min=1.5, T_max=20,   # expected period range
    rel_time=100,          # time to discard before the system reaches the limit cycle
    T_after_rel=10, timesteps_in_T=10, variables=None,  # optional; None = all variables
)
res.sel(quantity="period"), res.sel(quantity="amplitude"), res.sel(quantity="difference_rms")
```

- The time step is `T_min / timesteps_in_T`, so the period resolution is about that step.
  Increase `timesteps_in_T` for precision.
- **A single run at the current parameters** is a sweep over one value:
  `values=[Model.p.default]` (any parameter works as `parameter`).
- Read results per variable: `res["x"].sel(quantity="period").item()`. On the Dataset,
  `.values` is the dict method, not the data.
- Warnings mean that no period was found or confirmed, and **the returned value can still
  be off** (it falls back to the strongest spectral period). Try a longer `rel_time` or more
  `T_after_rel` periods.
- `difference_rms / amplitude` close to 0 indicates a clean limit cycle.

## Fitting parameters to data

Use this only when the user provides data to fit.

```python
from poincare.analysis import fit_result
from poincare.analysis.fits import make_target

target = make_target({Model.x: x_data, "E": e_data}, save_at=t_data)   # quantities allowed
fit = fit_result(
    sim,                     # may include transforms; target keys must match outputs
    target,
    p0={Model.k: (0.5, 0, 10),   # (initial guess, lower, upper)
        Model.x: 1.5},           # initial values can be fitted too
    scale={"E": 0.5},            # optional per-output residual weight
)
fit[Model.k]
```

- In 1.2.0, `fit_result` returns a dict `{component: best value}` and nothing else (no
  covariance). It calls `scipy.optimize.least_squares` (extra `**kwargs` are passed through).
- With units, give the data, `save_at` and `p0` as quantities. The result comes back as
  quantities.
- Use tight solver tolerances. Finite-difference Jacobians are noisy with the default 1e-3.
- If the data are on a different time grid than you want to simulate, `make_target` still
  defines the time points of the residual.

## Stochastic simulation (rebop)

Gillespie simulation of reaction networks (`MassAction` and `RateLaw` only) via the
`rebop` package (`pip install rebop`).

```python
from poincare.reactions.rebop import RebopSimulator   # also simbio.rebop, jablonski.rebop

rsim = RebopSimulator(Model).with_values({Model.A: 100})
ds = rsim.solve(upto_t=10, n_points=100, rng=1)   # n_points equal intervals → n_points + 1 rows
```

- Variables are integer copy numbers, and **values may not carry units** (only `upto_t`
  can). Models with plain `Equation`s (`x.derive() << ...`) are rejected.
- Rates may use `+ - * / **`, `real.exp`, `real.sqrt`, `real.hypot`, `real.degrees`,
  `real.radians` and the constants `real.e`, `real.pi`, `real.tau`.
- Average many runs (`xr.concat([... for seed in range(n)], dim="run").mean("run")`) before
  comparing with the ODE solution.
- For jablonski models with time-dependent excitation, use `jablonski.rebop.rebop_piecewise`
  (see [jablonski.md](jablonski.md#stochastic-runs)).
