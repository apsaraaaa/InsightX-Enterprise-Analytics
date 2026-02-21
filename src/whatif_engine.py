# src/whatif_engine.py

from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class WhatIfResult:
    base_value: float
    simulated_value: float
    delta_pct: float


class WhatIfEngine:
    """
    Deterministic what-if simulation using correlation elasticity.
    """

    @staticmethod
    def simulate(
        df: pd.DataFrame,
        driver_col: str,
        outcome_col: str,
        driver_change_pct: float
    ) -> WhatIfResult:

        if driver_col not in df or outcome_col not in df:
            raise ValueError("Selected columns not found in dataset")

        base_outcome = df[outcome_col].mean()

        corr = df[[driver_col, outcome_col]].corr().iloc[0, 1]
        elasticity = 0 if pd.isna(corr) else corr

        simulated = base_outcome * (1 + elasticity * driver_change_pct / 100)

        return WhatIfResult(
            base_value=base_outcome,
            simulated_value=simulated,
            delta_pct=((simulated / base_outcome) - 1) * 100
        )
