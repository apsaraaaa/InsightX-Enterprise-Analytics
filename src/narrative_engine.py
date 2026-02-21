# src/narrative_engine.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NarrativeContext:
    dataset_name: str
    rows: int
    columns: int
    quality_confidence: str
    missing_pct: float
    outliers: int
    num_insights: int
    forecast_growth_pct: Optional[float] = None


class NarrativeEngine:
    """
    Fully free, explainable AI narrative generator.
    No LLM, no API, no cost.
    """

    @staticmethod
    def generate(context: NarrativeContext) -> str:
        sections = []

        # --------------------------------------------------
        # EXECUTIVE SUMMARY
        # --------------------------------------------------
        sections.append(
            f"""
Executive Summary – {context.dataset_name}

The dataset contains {context.rows:,} records across {context.columns} features.
Overall data confidence is assessed as {context.quality_confidence.lower()}.

The analysis identified {context.num_insights} decision-relevant insights,
supporting executive-level reporting and performance monitoring.
""".strip()
        )

        # --------------------------------------------------
        # DATA RELIABILITY
        # --------------------------------------------------
        reliability = "strong" if context.missing_pct < 5 else "moderate"
        sections.append(
            f"""
Data Reliability Assessment

Data completeness is {reliability}, with missing values accounting for
approximately {context.missing_pct:.1f}% of the dataset.

Outlier analysis identified {context.outliers} anomalous observations,
which should be reviewed for business relevance.
""".strip()
        )

        # --------------------------------------------------
        # FORWARD OUTLOOK
        # --------------------------------------------------
        if context.forecast_growth_pct is not None:
            direction = (
                "positive"
                if context.forecast_growth_pct > 0
                else "negative"
            )
            sections.append(
                f"""
Forward Outlook

Trend extrapolation indicates a {direction} outlook, with an estimated
change of {context.forecast_growth_pct:.1f}% over the forecast horizon.
This projection supports planning and target-setting discussions.
""".strip()
            )

        # --------------------------------------------------
        # RECOMMENDATIONS
        # --------------------------------------------------
        sections.append(
            """
Recommendations

- Prioritize high-confidence metrics as executive KPIs.
- Monitor statistically sensitive variables for early risk signals.
- Use scenario modeling to assess strategic decisions.
- Review data quality periodically to maintain analytical reliability.
""".strip()
        )

        return "\n\n".join(sections)
