# poincare 1.2: declaring and simulating ODE systems

poincare is the base library. simbio and jablonski models are poincare `System`s,
so everything here applies to them too.

## Contents

- [Components](#components)
- [Equations](#equations)
- [Parameters, constants and functions](#parameters-constants-and-functions)
- [Composition (subsystems)](#composition-subsystems)
- [Simulator](#simulator)
- [Results](#results)
- [Reaction primitives](#reaction-primitives)
- [Reports and introspection](#reports-and-introspection)

## Components

```python
from poincare import (Constant, Derivative, Independent, Parameter, System, Variable,
                      assign, initial)

class Model(System):
    t = Independent()                               # time; only needed to use t in expressions
    x: Variable = initial(default=1)                # state variable, initial value
    v: Derivative = x.derive(initial=0)             # dx/dt as extra state (2nd-order systems)
    k: Parameter = assign(default=2)                # parameter (number, quantity or expression)
    c: Constant = assign(default=1, constant=True)  # constant; can set initial values
```

| Factory | Creates | Notes |
| --- | --- | --- |
| `initial(default=...)` | `Variable` | Default can be a number, a pint quantity or a `Constant` expression |
| `x.derive(initial=...)` | `Derivative` | Declares a higher-order state. Without `initial`, it is only used in equations |
| `assign(default=...)` | `Parameter` | Default can be an expression of other parameters, variables or time |
| `assign(default=..., constant=True)` | `Constant` | Use it for shared initial conditions (`initial(default=2 * c)`) |
| `Independent(default=0)` | time | One per system. `SpectroscopicSystem` already defines `time` in seconds |

**Annotate every component** (`x: Variable = ...`). The annotations build the keyword-only
constructor used for composition and `with_values`. An annotation that doesn't match the
component type raises `TypeError` when the class is created. Components with no default
(`assign()`) are required constructor arguments.

## Equations

```python
eq = x.derive() << -k * x       # dx/dt = -k x
force = v.derive() << -(w**2) * x
```

- `derivative << rhs` creates an `Equation`. Assign it to a class attribute (any name).
- **Several equations for the same derivative are summed.** Write each process as its own
  equation (production, degradation, …) rather than one long expression.
- Second-order systems need an explicit `v: Derivative = x.derive(initial=...)`.

## Parameters, constants and functions

- **Parameter defaults may be expressions**: `force: Parameter = assign(default=0.2 * real.sin(omega * t))`.
  Parameters that depend on variables or time are substituted into the equations.
- **Time- or variable-dependent parameters cannot be changed with `with_values`**
  (`ValueError: must recompile...`). Build a new simulator from an instance instead:
  `Simulator(Model(force=real.cos(Model.x)))`.
- Parameters that depend only on other parameters (for example a derived photon flux) *can*
  be changed through the parameters they depend on.
- **Math functions** come from `symbolite`: `from symbolite import real` gives `real.exp`,
  `real.log`, `real.sin`, `real.sqrt`, `real.expm1`, `real.tanh`, and others. Do not use
  `numpy` functions on symbolic components.
- **Pint quantities inside compiled expressions do not compile.** `rate * real.exp(-gap / (1 * u.boltzmann_constant * T))`
  fails with a `SyntaxError` at `Simulator(...)`. Put physical constants in a `Parameter`
  (`kB: Parameter = assign(default=1 * u.boltzmann_constant)`) and use that instead.
  A quantity as a component's *default value* is fine.

## Composition (subsystems)

A `System` can be instantiated inside another one. Keyword arguments link its components
to the outer components, and anything not passed is created per instance.

```python
class Damping(System):
    x: Variable = initial(default=0)
    vx: Derivative = x.derive(initial=0)
    gamma: Parameter = assign(default=0)
    damping = vx.derive() << -gamma * vx

class DampedOscillator(System):
    x: Variable = initial(default=1)
    vx: Derivative = x.derive(initial=0)
    k: Parameter = assign(default=1)
    gamma: Parameter = assign(default=0.1)
    spring = vx.derive() << -k * x
    damping = Damping(x=x, gamma=gamma)   # adds its equation to the same derivative
```

- Linked components share one state, and their equations add up.
- Unlinked components are named with the subsystem prefix. A variable shows up as
  `"sub.y"` in the results, and parameters as `sub.k`. Access them as
  `Outer.sub.component`, for example in `with_values({Outer.sub.k: 0.2})`. The output
  contains variables (and transforms), never parameters.
- Passing a number instead of a component sets that instance's default: `Damping(gamma=0.3)`.
- You can reuse one subsystem class many times (chains, networks). Each instance is
  independent unless linked.

## Simulator

```python
import numpy as np
from poincare import Simulator, solvers

sim = (
    Simulator(Model)                    # compiles once; accepts a class or an instance
    .with_solver(solvers.LSODA(rtol=1e-8, atol=1e-10))
    .with_values({Model.k: 3, Model.x: 2})
    .with_transform({"E": 0.5 * Model.v**2 + 0.5 * Model.x**2}, append=True)
)
result = sim.solve(save_at=np.linspace(0, 10, 101))
```

- **Immutable builder.** Every `with_*` returns a new simulator that shares the compiled
  function. Loops over values are cheap.
- `with_values(mapping, append=True)`: keys are components (`Model.k`, `Model.sub.x`).
  Values are numbers or pint quantities whose units must be compatible with the default's
  (otherwise `DimensionalityError`).
- `with_transform(mapping_or_list, append=False)` controls the output. **Without
  `append=True`, the output contains only the transform entries**, not the variables.
- `with_solver(solver)`: **the only way to choose the solver in 1.2.0.** The `solver=`
  argument of `Simulator(...)` is accepted but ignored.
  - Solvers: `solvers.LSODA` (default), `RK23`, `RK45`, `DOP853`, `Radau`, `BDF`. All are
    frozen dataclasses with `rtol` (default 1e-3), `atol` (1e-6), `first_step`, `max_step`.
  - The defaults give roughly 1e-3 relative error. **Set tolerances explicitly for
    quantitative work**, and for stiff systems (photophysics, kinetics with widely
    different rates) use LSODA, Radau or BDF.
- **`atol` is in SI base units**, because integration runs in base units (mol, m³, s,
  eV → J). Amounts like 1e-16 mol or volumes like 1e-15 m³ (1 pL) are invisible under the
  default `atol=1e-6`. The run then "succeeds" with nonsense (for example product exceeding
  substrate). Set `atol` a few orders below the smallest base-unit magnitude
  (`atol=1e-27` for ~1e-18 mol). Check conservation to confirm.
- `LSODA` with `save_at` starting at the start of `t_span`, and no events, uses scipy's
  `odeint` internally; otherwise it uses `solve_ivp`. If you see `Excess work done`, NaNs
  or a garbage trajectory, try `solvers.LSODA(..., implementation="LSODA")` (the
  `solve_ivp` path), `solvers.Radau` or `solvers.BDF`.
- **Debugging:** `prob = sim.create_problem()` exposes `prob.y` and `prob.p` (initial state
  and parameters in base units, ordered like `sim.compiled.variables` / `.parameters`)
  and `prob.rhs(t, y, p, dy)`, so you can evaluate the right-hand side by hand.
- `Simulator(Model, backend="numpy" | "numba" | "jax")`. numpy is the default. numba and
  jax must be installed separately (jax is not available on Windows).
- `solve(save_at=..., t_span=None, events=(), check_dimensionality=True)`:
  - With units, `save_at` must be a time quantity (`np.linspace(0, 10, 101) * u.s`).
    Without units, it must be a plain array.
  - `t_span` defaults to `(0, save_at[-1])`.
  - `events` takes `scipy_events` events (`Event(condition=..., terminal=True)`).
- `sim.interact(values={Model.k: (0, 10, 0.1)}, save_at=...)` gives ipywidgets sliders in
  Jupyter. In marimo, put a `mo.ui.slider` value into `with_values` instead.

## Results

`solve` returns an `xarray.Dataset` indexed by `time`, with one data variable per output.
Subsystem variables are named with dots (`"sub.x"`).

```python
result["x"]                                   # DataArray (pint-aware if the model has units)
result.pint.dequantify().to_dataframe()       # strip units → pandas (needed for .plot())
result["x"].pint.to(u.mm).pint.dequantify().values
result.to_dataframe().plot()                  # unitless models
```

The time coordinate keeps the unit of `save_at` (for example ms). In scripts without a
display, save figures (`plt.savefig(...)`) instead of calling `plt.show()`, or set
`MPLBACKEND=Agg`.

## Reaction primitives

`poincare.reactions` defines `Reactant`, `reaction_initial`, `RateLaw`, `MassAction` and
`AbsoluteRateLaw`. simbio re-exports and extends them, and jablonski transitions wrap
`MassAction`. Usage is documented in [simbio.md](simbio.md#reactions).

## Reports and introspection

- `print(Model)` or `Model` in a notebook shows a table of variables, parameters and equations.
- `Model.k.default` (parameters and constants) and `Model.x.initial` (variables) give the
  declared defaults, which is useful for analytic checks.
- `Model.variables` and `Model.parameters` return `xarray.DataArray`s of components.
- `model_report(Model, path=None, transform={Model.k: "k_1"}, descriptions=None,
  standalone=True, replace_algebraics=False)` returns (or writes to `path`) a LaTeX report
  with equations, a variable table and a parameter table.
  - simbio's `model_report` adds a reactions section.
  - jablonski's (`jablonski.plots.model_report`) adds a Jablonski diagram.
- Lower-level LaTeX helpers live in `poincare.printing.latex`: `latex_equations`,
  `parameter_table`, `variable_table`, `ToLatex`.
- `poincare.helpers.get_from("sub.k", Model)` resolves a dotted name to a component, and
  `to_values({"sub.k": 2}, Model)` turns a dict of dotted names into a `with_values` mapping.
