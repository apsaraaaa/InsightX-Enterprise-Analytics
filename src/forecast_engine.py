# src/forecast_engine.py

from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ForecastResult:
    history: pd.DataFrame
    forecast: pd.DataFrame
    metric: str
    frequency: str


class ForecastEngine:
    """
    Lightweight, production-safe forecasting engine.
    Uses moving average + trend extrapolation.
    """

    @staticmethod
    def prepare_time_series(
        df: pd.DataFrame,
        date_col: str,
        target_col: str,
        freq: str
    ) -> pd.DataFrame:
        ts = (
            df[[date_col, target_col]]
            .dropna()
            .rename(columns={date_col: "ds", target_col: "y"})
        )

        ts["ds"] = pd.to_datetime(ts["ds"])
        ts = ts.set_index("ds").resample(freq).sum().reset_index()

        return ts

    @staticmethod
    def forecast(
        ts: pd.DataFrame,
        periods: int,
        window: int = 3
    ) -> ForecastResult:
        history = ts.copy()

        # Moving average trend
        history["trend"] = history["y"].rolling(window).mean()

        last_date = history["ds"].iloc[-1]
        last_trend = history["trend"].dropna().iloc[-1]

        future_dates = pd.date_range(
            start=last_date,
            periods=periods + 1,
            freq=pd.infer_freq(history["ds"])
        )[1:]

        forecast_values = [
            last_trend * (1 + 0.02 * i) for i in range(1, periods + 1)
        ]

        forecast_df = pd.DataFrame({
            "ds": future_dates,
            "y": forecast_values
        })

        return ForecastResult(
            history=history,
            forecast=forecast_df,
            metric="y",
            frequency=pd.infer_freq(history["ds"])
        )
