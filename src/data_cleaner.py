from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Dict, Any
from dataclasses import dataclass
import logging

# ---------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# DATA QUALITY REPORT
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class DataQualityReport:
    """
    Immutable container for data quality assessment.
    Safe to use across dashboards, insights, and reports.
    """
    rows: int
    columns: int
    total_cells: int
    missing_cells: int
    missing_pct: float
    duplicate_rows: int
    outlier_cells: int
    quality_score: float
    confidence_level: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows": self.rows,
            "columns": self.columns,
            "total_cells": self.total_cells,
            "missing_cells": self.missing_cells,
            "missing_pct": self.missing_pct,
            "duplicate_rows": self.duplicate_rows,
            "outlier_cells": self.outlier_cells,
            "quality_score": self.quality_score,
            "confidence_level": self.confidence_level,
        }

# ---------------------------------------------------------------------
# DATA CLEANER & QUALITY ENGINE
# ---------------------------------------------------------------------
class DataCleaner:
    """
    Enterprise-grade data quality engine.

    Responsibilities:
    - Completeness analysis
    - Duplicate detection
    - Robust outlier detection (IQR)
    - Explainable quality scoring
    - Business confidence mapping
    """

    # Weights must sum to 1.0
    WEIGHTS = {
        "missing": 0.5,
        "duplicates": 0.3,
        "outliers": 0.2,
    }

    # =========================================================
    # PUBLIC API (COMPATIBILITY GUARANTEED)
    # =========================================================
    @classmethod
    def analyze(cls, df: pd.DataFrame) -> DataQualityReport:
        """
        Public method expected by the app.
        This guarantees ZERO integration errors.
        """
        return cls.generate_quality_report(df)

    @classmethod
    def run(cls, df: pd.DataFrame) -> DataQualityReport:
        """
        Alias for compatibility with alternative pipelines.
        """
        return cls.generate_quality_report(df)

    # =========================================================
    # CORE QUALITY ENGINE
    # =========================================================
    @classmethod
    def generate_quality_report(cls, df: pd.DataFrame) -> DataQualityReport:
        if df is None or df.empty:
            raise ValueError("Cannot generate quality report for empty dataset")

        rows, columns = df.shape
        total_cells = rows * columns

        # ------------------------------
        # Missing values
        # ------------------------------
        missing_cells = int(df.isna().sum().sum())
        missing_pct = round((missing_cells / total_cells) * 100, 2)

        # ------------------------------
        # Duplicate rows
        # ------------------------------
        duplicate_rows = int(df.duplicated().sum())

        # ------------------------------
        # Outlier detection
        # ------------------------------
        outlier_cells = cls._count_outliers(df)

        # ------------------------------
        # Quality score
        # ------------------------------
        quality_score = cls._calculate_quality_score(
            missing_pct=missing_pct,
            duplicate_rows=duplicate_rows,
            outlier_cells=outlier_cells,
            total_cells=total_cells,
        )

        confidence = cls._confidence_from_score(quality_score)

        report = DataQualityReport(
            rows=rows,
            columns=columns,
            total_cells=total_cells,
            missing_cells=missing_cells,
            missing_pct=missing_pct,
            duplicate_rows=duplicate_rows,
            outlier_cells=outlier_cells,
            quality_score=quality_score,
            confidence_level=confidence,
        )

        logger.info(
            f"Data quality computed | Score={quality_score}, Confidence={confidence}"
        )

        return report

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    @staticmethod
    def _count_outliers(df: pd.DataFrame) -> int:
        """
        Count outlier cells using robust IQR method.
        Only numeric columns are considered.
        """
        outlier_count = 0
        numeric_df = df.select_dtypes(include=["number"])

        if numeric_df.empty:
            return 0

        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if series.empty:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            if iqr == 0:
                continue

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outlier_count += int(((series < lower) | (series > upper)).sum())

        return outlier_count

    @classmethod
    def _calculate_quality_score(
        cls,
        missing_pct: float,
        duplicate_rows: int,
        outlier_cells: int,
        total_cells: int,
    ) -> float:
        """
        Explainable weighted quality score (0–100).
        """
        missing_penalty = missing_pct * cls.WEIGHTS["missing"]

        duplicate_penalty = (
            (duplicate_rows / max(1, total_cells)) * 100
        ) * cls.WEIGHTS["duplicates"]

        outlier_penalty = (
            (outlier_cells / max(1, total_cells)) * 100
        ) * cls.WEIGHTS["outliers"]

        score = 100 - (missing_penalty + duplicate_penalty + outlier_penalty)

        return round(max(score, 0), 1)

    @staticmethod
    def _confidence_from_score(score: float) -> str:
        """
        Map numeric score to business-friendly confidence.
        """
        if score >= 85:
            return "High"
        elif score >= 65:
            return "Medium"
        else:
            return "Low"
