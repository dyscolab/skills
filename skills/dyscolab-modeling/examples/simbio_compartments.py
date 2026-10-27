"""Reversible binding A + B <-> AB in a simbio Compartment.

Checks: mass conservation, the analytic equilibrium, and that tracking AB as an
amount in a 2 L compartment gives the same concentration as tracking it as a
concentration.
"""

import numpy as np
import pint

from poincare import SteadyState, solvers  # simbio does not re-export these
from simbio import (
    Compartment,
    MassAction,
    Parameter,
    Simulator,
    Species,
    Volume,
    amount,
    assign,
    concentration,
    volume,
)
from simbio.reactions import ReversibleSynthesis

u = pint.get_application_registry()
TIGHT = solvers.LSODA(rtol=1e-9, atol=1e-12)


class Binding(Compartment):
    V: Volume = volume(default=2 * u.L)
    A: Species = concentration(default=1 * u.mM)
    B: Species = concentration(default=0.5 * u.mM)
    AB: Species = concentration(default=0 * u.mM)
    kon: Parameter = assign(default=1 / u.mM / u.s)
    koff: Parameter = assign(default=0.1 / u.s)

    binding = ReversibleSynthesis(A=A, B=B, AB=AB, forward_rate=kon, reverse_rate=koff)


class BindingAmountAB(Compartment):
    """Same system, but AB is tracked as an amount (mmol) instead of a concentration.

    With amount species, write the reactions directly in the Compartment.
    Motifs from simbio.reactions are subsystems and do not see the compartment
    volume (simbio 1.2.0): with units they fail, without units they silently
    skip the volume conversion.
    """

    V: Volume = volume(default=2 * u.L)
    A: Species = concentration(default=1 * u.mM)
    B: Species = concentration(default=0.5 * u.mM)
    AB: Species = amount(default=0 * u.mmol)
    kon: Parameter = assign(default=1 / u.mM / u.s)
    koff: Parameter = assign(default=0.1 / u.s)

    binding = MassAction(reactants=[A, B], products=[AB], rate=kon)
    unbinding = MassAction(reactants=[AB], products=[A, B], rate=koff)


save_at = np.linspace(0, 30, 61) * u.s
conc = Simulator(Binding).with_solver(TIGHT).solve(save_at=save_at)

# Conservation: A + AB and B + AB are constant.
total_A = (conc["A"] + conc["AB"]).pint.to(u.mM).pint.dequantify().values
np.testing.assert_allclose(total_A, 1.0, rtol=1e-8)

# Equilibrium: AB = (A0 - AB)(B0 - AB) / Kd, with Kd = koff / kon = 0.1 mM.
a0, b0, kd = 1.0, 0.5, 0.1
ab_eq = ((a0 + b0 + kd) - np.sqrt((a0 + b0 + kd) ** 2 - 4 * a0 * b0)) / 2
steady = SteadyState().solve(Simulator(Binding).with_solver(TIGHT))
np.testing.assert_allclose(steady["AB"].pint.to(u.mM).pint.dequantify().item(), ab_eq, rtol=1e-6)

# Amount vs concentration bookkeeping: AB_amount / V == AB_concentration.
amt = (
    Simulator(BindingAmountAB)
    .with_solver(TIGHT)
    .with_transform({"AB_conc": BindingAmountAB.AB / BindingAmountAB.V}, append=True)
    .solve(save_at=save_at)
)
np.testing.assert_allclose(
    amt["AB_conc"].pint.to(u.mM).pint.dequantify().values,
    conc["AB"].pint.to(u.mM).pint.dequantify().values,
    rtol=1e-6,
    atol=1e-12,
)

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    conc.pint.dequantify().to_dataframe()[["A", "B", "AB"]].plot()
    plt.show()
