# simbio 1.2: chemical reaction networks

simbio models are poincare `System`s. `simbio` re-exports `System`, `Variable`,
`Parameter`, `Constant`, `Independent`, `Simulator`, `initial`, `assign`, the reaction
primitives and `model_report`. It does **not** re-export `SteadyState`, `Oscillations`
or `solvers`, so import those from `poincare`.

## Contents

- [Reactions](#reactions)
- [Reaction motifs](#reaction-motifs)
- [Compartments and volume](#compartments-and-volume)
- [SBML, BioModels and MathML](#sbml-biomodels-and-mathml)
- [Graphs, reports, stochastic runs](#graphs-reports-stochastic-runs)

## Reactions

```python
from simbio import MassAction, RateLaw, AbsoluteRateLaw, System, Variable, Parameter, initial, assign

class Network(System):
    A: Variable = initial(default=1)
    B: Variable = initial(default=1)
    C: Variable = initial(default=0)
    k: Parameter = assign(default=0.5)

    r1 = MassAction(reactants=[2 * A, B], products=[C], rate=k)   # rate = k·A²·B
    r2 = RateLaw(reactants=[C], products=[], rate_law=0.1 * C / (1 + C))  # any rate law
    feed = RateLaw(reactants=[], products=[A], rate_law=0.2)       # zero-order creation
```

- **Stoichiometry by multiplication:** `2 * A` means coefficient 2. Empty `reactants`
  gives creation, and empty `products` gives degradation.
- `MassAction(rate=k)`: the rate law is `k · Π reactant^stoichiometry`, and each species
  changes by `±stoichiometry · rate law`.
- `RateLaw(rate_law=expr)`: you supply the full rate law (Hill, Michaelis–Menten,
  inhibition…), interpreted as concentration/time.
- `AbsoluteRateLaw(rate_law=expr)`: the rate law is amount/time. It only differs from
  `RateLaw` inside a `Compartment`.
- **Modulators (catalysts, repressors)** that appear in a rate law but are not consumed
  can be listed on both sides (`reactants=[p], products=[m, p]`). That keeps them visible
  to stochastic simulation and to the reaction graph. For ODEs alone it is optional.
- Reactions combine with plain poincare equations on the same model
  (`x.derive() << ...`). Rates add up.
- A pint quantity as `rate`/`rate_law` is wrapped automatically in a hidden parameter
  named `_<reaction>_rate_law`. Declare a named `Parameter` instead when you want to change
  it with `with_values`.

## Reaction motifs

`simbio.reactions` provides `System`s with `Reactant` fields (link them with keywords):

| Motif | Scheme | Arguments |
| --- | --- | --- |
| `Creation` | ∅ → A | `A, rate` |
| `AutoCreation` | A → 2A | `A, rate` |
| `Destruction` | A → ∅ | `A, rate` |
| `Conversion` | A → B | `A, B, rate` |
| `Synthesis` | A + B → AB | `A, B, AB, rate` |
| `Dissociation` | AB → A + B | `AB, A, B, rate` |
| `ReversibleSynthesis` | A + B ⇌ AB | `A, B, AB, forward_rate, reverse_rate` |
| `Equilibration` | A ⇌ B | `A, B, forward_rate, reverse_rate` |
| `CatalyzeConvert` | A + B ⇌ A:B → P | `A, B, AB, P, forward_rate, reverse_rate, conversion_rate` |
| `MichaelisMenten` | E + S ⇌ ES → E + P (mass action) | `E, S, ES, P, forward_rate, reverse_rate, catalytic_rate` |
| `MichaelisMentenEqApprox` | S → P, `v = Vmax·S/(Kd + S)` | `S, P, maximum_velocity, dissociation_constant` |
| `MichaelisMentenQuasiSSAprox` | S → P, `v = Vmax·S/(Km + S)` | `S, P, maximum_velocity, michaelis_constant` |

```python
from simbio.reactions import Destruction, ReversibleSynthesis, Synthesis

class Model(System):
    A: Variable = initial(default=10)
    B: Variable = initial(default=5)
    AB: Variable = initial(default=0)
    binding = ReversibleSynthesis(A=A, B=B, AB=AB, forward_rate=1, reverse_rate=0.1)
    decay = Destruction(A=AB, rate=0.01)
    dimer = Synthesis(A=2 * A, B=B, AB=AB, rate=2)   # scale stoichiometry from outside
```

All motif kinetics are mass action unless stated otherwise. `MichaelisMenten.to_eq_approx()`
and `to_qss_approx()` raise `NotImplementedError` in 1.2.0.

**Writing your own motif:** declare `Reactant` fields with `reaction_initial()` and rates
with `assign()`, then combine them with `MassAction`/`RateLaw`. Use `S.variable` in rate
law expressions:

```python
from simbio import Reactant, reaction_initial

class HillActivation(System):
    """Activator X drives ∅ -> Y with a Hill rate law."""
    X: Reactant = reaction_initial()
    Y: Reactant = reaction_initial()
    vmax: Parameter = assign(default=1)
    K: Parameter = assign(default=1)
    n: Parameter = assign(default=2)
    reaction = RateLaw(reactants=[X], products=[X, Y],
                       rate_law=vmax * X.variable**n / (K**n + X.variable**n))
```

## Compartments and volume

```python
from simbio import (Compartment, Species, Volume, amount, concentration, volume,
                    MassAction, RateLaw, AbsoluteRateLaw, Parameter, assign)

class Cell(Compartment):
    V: Volume = volume(default=2 * u.L)              # exactly one Volume per Compartment
    A: Species = concentration(default=2 * u.mM)     # tracked as concentration
    B: Species = amount(default=3 * u.mmol)          # tracked as amount
    AB: Species = concentration(default=0 * u.mM)
    kon: Parameter = assign(default=1 / u.mM / u.s)
    binding = MassAction(reactants=[A, B], products=[AB], rate=kon)
```

How simbio converts with the compartment volume `V`:

| Reaction type | Concentration species | Amount species |
| --- | --- | --- |
| `RateLaw` / `MassAction` (concentration/time) | as written | × V |
| `AbsoluteRateLaw` (amount/time) | ÷ V | as written |
| Inside a `MassAction` rate law | used as is | divided by V (→ concentration) |

Rules and pitfalls:

- A `Compartment` needs **exactly one** `Volume`. Zero or two raises `AttributeError`.
- **Inside a Compartment with amount species, write reactions directly with `MassAction`,
  `RateLaw` and `AbsoluteRateLaw`.**
  - Motifs from `simbio.reactions` are subsystems and don't see the compartment volume.
  - With units they fail (`PintError: Units are defined inconsistently`).
  - Without units they **silently skip the volume conversion**.
  - Motifs are fine when all species are concentrations, because no conversion is needed.
- `Volume` is a variable. Give it an equation for growing compartments:
  `growth = V.derive() << rate`. A *concentration* species keeps its concentration as `V`
  grows, which effectively creates matter. Track amounts and report concentrations with a
  transform (`with_transform({"A_conc": Cell.A / Cell.V}, append=True)`).
- Growing cell, Michaelis–Menten with amounts (tested pattern):

  ```python
  class Cell(Compartment):
      V: Volume = volume(default=1 * u.pL)
      E: Species = amount(default=1e-18 * u.mol)
      S: Species = amount(default=1e-16 * u.mol)
      ES: Species = amount(default=0 * u.mol)
      P: Species = amount(default=0 * u.mol)
      growth_rate: Parameter = assign(default=0.1 * u.pL / u.min)
      growth = V.derive() << growth_rate
      binding = MassAction(reactants=[E, S], products=[ES], rate=1e6 / u.M / u.s)
      unbinding = MassAction(reactants=[ES], products=[E, S], rate=1 / u.s)
      catalysis = MassAction(reactants=[ES], products=[E, P], rate=10 / u.s)

  sim = (Simulator(Cell)
         .with_solver(solvers.LSODA(rtol=1e-9, atol=1e-27))   # atol in mol / m³
         .with_transform({"P_conc": Cell.P / Cell.V}, append=True))
  ```

  Setting `growth_rate` to 0 with `with_values` gives the constant-volume limit.
- Compartments can be nested, but **their `Species` and `Volume` cannot be linked to
  outside components** (`TypeError`). Only initial values (numbers or quantities) and
  plain `Parameter`s/`Variable`s can be passed: `Inner(A=5, T=outer_T)`.
- `reaction_amount()` and `reaction_concentration()` create `Reactant` fields backed by
  `Species`, for motif-style subsystems.

## SBML, BioModels and MathML

These need `pip install "simbio[io]"`, which provides `python-libsbml` and `biomodels`.

**Known 1.2.0 bug:** `simbio.io.sbml` and `simbio.io.mathML` fail at import on
Python < 3.14 (`NameError: name 'types' is not defined`). Use Python 3.14, or tell the user
that SBML import needs a newer simbio or Python. Fixed in newer simbio (not on PyPI yet),
which also fixes the import of MathML function definitions.

```python
from simbio.io import sbml, biomodels

Model = sbml.load("model.xml")                       # returns a System class
Model = sbml.loads(text, name="MyModel")             # name required if the SBML has none
Model = biomodels.load("BIOMD0000000012")            # downloads from BioModels (network)
sim = Simulator(Model)                               # simulate like any other model
Model.k1, Model.X                                    # components named after SBML ids
```

- `load(path, *, name=None, identity_mapper=...)`.
- `loads(text, *, name=None, identity_mapper=..., ignore_namespaces=[])`.
- `biomodels.load(model_id, *, name=None, ignore_namespaces=[])`.
- `print(Model)` lists the imported variables, parameters (including compartments) and
  reactions.
- Imported models usually have no pint units. Time is in the model's SBML time units
  (seconds unless the file says otherwise), so pass plain `save_at` arrays.
- Imported species are plain `Variable`s (not `Species` in `Compartment`s), so volume
  conversions are handled the way the SBML specifies them.
- The SBML packages `comp`, `fbc`, `groups`, `multi` and `qual`, and a global
  conversion factor, raise `NotImplementedError`. `layout`/`render` are ignored. Pass
  `ignore_namespaces=["fbc"]` (for example) to skip a package deliberately.
- MathML helpers (low level, libsbml AST ↔ symbolite): `simbio.io.mathML.to_mathML(expr)`
  and `simbio.io.mathML.mathMLImporter().convert(node)`.
- `simbio.io.sbml.substitute_by_name.substitute_by_name(expr, **{"name": value})`
  substitutes symbols by name in an expression. In newer simbio the module moved to
  `simbio.io.substitute_by_name`.

## Graphs, reports, stochastic runs

- `from simbio.io.graph.networkx import graph, to_Variable_graph, to_reaction_graph`:
  - `graph(Model)` builds a bipartite `networkx.DiGraph` of variables and reactions, with
    `stoichiometry` edge attributes.
  - The projections give species–species or reaction–reaction graphs.
  - Needs `networkx`.
- `simbio.model_report(Model, path=None, ...)` gives a LaTeX report with a reactions section
  (same arguments as poincare's).
- `simbio.notebook_report(Model, show=True, ...)` is the notebook version (Jupyter or
  marimo): reactions, then equations, variables and parameters, as Markdown (same arguments
  as `poincare.printing.notebook_report`). Requires simbio and poincare newer than the
  current PyPI releases.
- `simbio.latex.latex_reactions(Model)` returns only the reactions block as LaTeX. Newer
  simbio takes `format="markdown"` for `$$` display math.
- `from simbio.rebop import RebopSimulator` runs Gillespie simulations. See
  [analysis.md](analysis.md#stochastic-simulation-rebop). Copy numbers must be unitless
  integers.
