from __future__ import annotations

import pandas as pd
from typing import Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# -------------------------------------------------
# DATA STRUCTURES
# -------------------------------------------------
@dataclass(frozen=True)
class NumericStats:
    mean: float
    median: float
    std: float
    min: float
    max: float
    skewness: float
    kurtosis: float


@dataclass(frozen=True)
class EDASummary:
    numeric_summary: Dict[str, NumericStats]
    categorical_distribution: Dict[str, Dict[str, float]]
    correlation_matrix: Dict[str, Dict[str, float]]
    strong_correlations: List[str]
    potential_kpis: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "numeric_summary": {
                k: vars(v) for k, v in self.numeric_summary.items()
            },
            "categorical_distribution": self.categorical_distribution,
            "correlation_matrix": self.correlation_matrix,
            "strong_correlations": self.strong_correlations,
            "potential_kpis": self.potential_kpis,
        }


# -------------------------------------------------
# EDA ENGINE (PUBLIC API)
# -------------------------------------------------
class EDAEngine:
    """
    Single source of truth for EDA logic.
    """

    @classmethod
    def run(cls, df: pd.DataFrame) -> EDASummary:
        if df is None or df.empty:
            raise ValueError("Cannot run EDA on empty dataframe")

        logger.info("Running EDA")

        numeric = cls._numeric(df)
        categorical = cls._categorical(df)
        corr = cls._correlation(df)
        strong = cls._strong_correlations(corr)
        kpis = cls._identify_kpis(df, numeric)

        return EDASummary(
            numeric_summary=numeric,
            categorical_distribution=categorical,
            correlation_matrix=corr,
            strong_correlations=strong,
            potential_kpis=kpis,
        )

    # ---------------- INTERNAL ----------------
    @staticmethod
    def _numeric(df: pd.DataFrame) -> Dict[str, NumericStats]:
        result = {}
        for col in df.select_dtypes(include="number").columns:
            s = df[col].dropna()
            if s.nunique() <= 1:
                continue
            result[col] = NumericStats(
                mean=round(s.mean(), 4),
                median=round(s.median(), 4),
                std=round(s.std(), 4),
                min=round(s.min(), 4),
                max=round(s.max(), 4),
                skewness=round(s.skew(), 4),
                kurtosis=round(s.kurtosis(), 4),
            )
        return result

    @staticmethod
    def _categorical(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        dist = {}
        for col in df.select_dtypes(exclude="number").columns:
            vc = df[col].astype(str).value_counts(normalize=True).head(10)
            dist[col] = {k: round(v * 100, 2) for k, v in vc.items()}
        return dist

    @staticmethod
    def _correlation(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        num = df.select_dtypes(include="number")
        if num.shape[1] < 2:
            return {}
        corr = num.corr()
        return {
            c: {k: round(v, 3) for k, v in corr[c].items()}
            for c in corr.columns
        }

    @staticmethod
    def _strong_correlations(
        corr: Dict[str, Dict[str, float]], threshold: float = 0.7
    ) -> List[str]:
        pairs = []
        for a, rel in corr.items():
            for b, v in rel.items():
                if a != b and abs(v) >= threshold:
                    pairs.append(f"{a} ↔ {b} (r={v})")
        return list(set(pairs))

    @staticmethod
    def _identify_kpis(
        df: pd.DataFrame, stats: Dict[str, NumericStats]
    ) -> List[str]:
        return [
            c for c, s in stats.items()
            if abs(s.skewness) < 2 and s.std > 0
        ]
