# Workflows: scope, file layout and model conventions

## Do the requested stage, not the whole pipeline

| Request | Deliver | Don't add |
| --- | --- | --- |
| "Declare / write / implement a model of X" | The model, plus proof that it works: a model report (`notebook_report` in a notebook) and one short example simulation with a plot | Sweeps, fits, steady-state scans, comparisons with literature |
| "Simulate X" (under conditions Y) | Model (if missing), that simulation, one plot or summary | Extra scenarios nobody asked for |
| "Find the steady state / sweep / bifurcation / period" | That analysis on the existing model | Fits, reports |
| "Fit to this data" | Fit using the data the user supplied | Data the user did not supply |
| "Report / write up the model" | `model_report` LaTeX, or a short description | New simulations |

- **Compare with data only when the user provides it** (a file, an array, or numbers in the
  message). Never search the literature, invent "typical experimental" curves, or digitize
  published figures unprompted. If parameter values are missing, use clearly labelled
  placeholders and say so. Don't stop to research them.
- **Sanity checks are part of a correct model, not extra analysis.** Keep them
  cheap: check that units are consistent, that conserved totals stay constant, and run one
  limiting case with a known answer. Report the outcome in one line.
- When the user later asks for more, build on the existing files rather than starting over.

## Showing that a declared model works

A model report is the quickest way for the user to check that the code matches the
equations they had in mind. Prefer a notebook (Jupyter or marimo) with:

```python
# cell 1: the report (renders Markdown + LaTeX in Jupyter and marimo)
from poincare.printing import notebook_report  # simbio: from simbio import notebook_report
notebook_report(MyModel)                       # jablonski: from jablonski.plots import notebook_report

# cell 2: one example simulation
result = sim.solve(save_at=...)
result.pint.dequantify().to_dataframe().plot()
```

- `notebook_report(Model, show=False)` returns the Markdown string instead of displaying
  it, for example to save it to a `.md` file.
- simbio's `notebook_report` starts with a reactions section, and jablonski's
  (`jablonski.plots.notebook_report`) starts with the Jablonski diagram, so use the one from
  the library the model is built with.
- In scripts, `print(model_report(Model))` gives the LaTeX source, or use
  `model_report(Model, path="model.tex")`.
- For a larger model in `model.py`, the notebook imports it (see File layout below), so the
  report always reflects the current model file.

## File layout

**Small models** (a handful of states and equations): put the model and its example run in
one script or notebook.

**Larger models** (many states or parameters, several transitions or reactions, or a model
reused by several analyses): keep the declaration and the analysis apart.

```
model.py            # (or models/…) System classes only: no simulation at import time
analysis.ipynb      # or analysis.py: imports the model, configures Simulators, runs things
```

Making the import work, in this order of preference:

1. If the project already has a package or `pyproject.toml`, put the model in it and
   install the project (editable) into the environment the user already uses.
2. If the model file sits next to the notebook or script, `from model import MyModel` works
   from the notebook directory.
3. If the notebook is in a subfolder, add the model's folder in the first cell:

   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path("..").resolve()))   # folder containing model.py
   from model import MyModel
   ```

Do not create `pyproject.toml`, `src/` layouts, data folders or environment files unless the
user asks for them or they already exist.

**Full research projects** (only when the user is building one): a small package with model
modules and custom transitions or reactions, notebooks per analysis or figure that import it,
and a folder for the *user's* data files.

## Model conventions for larger models

- **One place for parameters.** Declare every rate and physical constant as a named
  `Parameter` with units and a short comment giving its meaning and source:
  `k_r6: Parameter = assign(default=1510 / u.s)  # 4S3/2 radiative, Anderson 2013 Table 2`.
  Unknown values get a placeholder and a `# TODO: value not reported` comment.
- **Derived quantities are expressions**, not duplicated numbers:
  `photon_flux = power_density / (h * c / wavelength)`, `initial(default=yb_fraction * (1 - isolated))`.
  Changing the base parameter with `with_values` updates everything that depends on it.
- **Control parameters** (power, temperature, wavelength) are `Parameter`s with defaults,
  so experiments only call `with_values` or set `piecewise` events.
- **Reusable mechanisms become small `System` classes** (custom transitions, reaction
  motifs, coupling terms) that are instantiated with keyword links. Avoid copy-pasting
  equations.
- **Name states and transitions physically** (`Er_4S3_2`, `etu_13`, `green_decay`). The
  names become the output columns and the `line_<name>` emission keys.

## Running experiments

- Build one base simulator, `Simulator(Model).with_solver(solvers.LSODA(rtol=..., atol=...))`,
  and derive variants with `with_values` / `with_transform(..., append=True)`. Don't
  re-create simulators in loops (that recompiles).
- Time-dependent protocols (pulses, steps, temperature jumps): use jablonski's `piecewise`
  for photophysics. For plain poincare/simbio models, run consecutive `solve` calls,
  passing the final state on with `with_values`, or use a time-dependent `Parameter`
  expression.
- Scans: use the loop + `xr.concat` pattern ([analysis.md](analysis.md#parameter-sweeps)),
  and nest it or concat on a second dimension for 2D scans.
- Plot with `result.pint.dequantify().to_dataframe().plot()` or xarray's `.plot()`. Label
  axes with units.

## Validation

- **Analytic limits:** single-exponential decay (τ = 1/Σk), two-level steady state
  `k_abs/(k_abs + k_decay)`, Boltzmann ratios `g·exp(-ΔE/kT)` between fast-exchanging levels,
  quantum yield `k_r/Σk`, Michaelis–Menten initial rate, equilibrium constants.
- **Conservation:** total population of each species or ion, or total mass in closed
  networks. Assert it is constant within the solver tolerance.
- **Scaling laws:** for example an n-photon process scales as Pⁿ at low power.
- **Units:** run the model with units at least once. pint catches inconsistent rate
  dimensions.
- Use `np.testing.assert_allclose` with explicit `rtol`, set solver tolerances well below
  it, and dequantify only after converting to a known unit.
