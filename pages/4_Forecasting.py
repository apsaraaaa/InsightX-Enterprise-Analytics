# pages/4_Forecasting.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.forecast_engine import ForecastEngine

st.set_page_config(page_title="InsightX | Forecasting Intelligence", layout="wide")

# --------------------------------------------------
# DATA GUARD
# --------------------------------------------------
if (
    "df" not in st.session_state
    or st.session_state.df is None
    or not st.session_state.data_locked
):
    st.warning("Complete Data Intake before Forecasting.")
    st.stop()

df = st.session_state.df.copy()

st.title("Advanced Forecasting Intelligence")
st.caption("Revenue, Product Demand & Customer Risk Forecasting")

st.divider()

# --------------------------------------------------
# DETECT COLUMNS
# --------------------------------------------------
date_cols = [c for c in df.columns if "date" in c.lower()]
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

if not date_cols or not numeric_cols:
    st.error("Requires at least one date column and numeric metric.")
    st.stop()

date_col = date_cols[0]
metric_col = df[numeric_cols].sum().idxmax()

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# --------------------------------------------------
# FORECAST MODE SELECTOR
# --------------------------------------------------
forecast_mode = st.selectbox(
    "Select Forecast Type",
    [
        "Company Revenue Forecast",
        "Product Line Forecast",
        "Customer Revenue Risk Forecast"
    ]
)

horizon = st.slider("Forecast Horizon (Periods)", 3, 24, 6)

freq_map = {"Monthly": "M", "Quarterly": "Q", "Yearly": "Y"}
freq_label = st.selectbox("Aggregation Level", list(freq_map.keys()))
freq = freq_map[freq_label]

st.divider()

# ==================================================
# 1️⃣ COMPANY REVENUE FORECAST
# ==================================================
if forecast_mode == "Company Revenue Forecast":

    st.subheader("Company Revenue Forecast")

    ts = ForecastEngine.prepare_time_series(
        df=df,
        date_col=date_col,
        target_col=metric_col,
        freq=freq
    )

    result = ForecastEngine.forecast(ts=ts, periods=horizon)

    last_actual = result.history["y"].iloc[-1]
    forecast_value = result.forecast["y"].iloc[-1]
    growth_pct = ((forecast_value / last_actual) - 1) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("Last Actual", f"{last_actual:,.2f}")
    c2.metric("Forecasted", f"{forecast_value:,.2f}")
    c3.metric("Projected Change", f"{growth_pct:.1f}%")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=result.history["ds"],
        y=result.history["y"],
        name="Historical",
        mode="lines"
    ))
    fig.add_trace(go.Scatter(
        x=result.forecast["ds"],
        y=result.forecast["y"],
        name="Forecast",
        mode="lines",
        line=dict(dash="dash")
    ))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# 2️⃣ PRODUCT LINE FORECAST
# ==================================================
elif forecast_mode == "Product Line Forecast":

    product_cols = [c for c in categorical_cols if "product" in c.lower()]

    if not product_cols:
        st.warning("No product column detected.")
    else:
        product_col = product_cols[0]
        product_choice = st.selectbox(
            "Select Product Line",
            df[product_col].unique()
        )

        filtered_df = df[df[product_col] == product_choice]

        ts = ForecastEngine.prepare_time_series(
            df=filtered_df,
            date_col=date_col,
            target_col=metric_col,
            freq=freq
        )

        result = ForecastEngine.forecast(ts=ts, periods=horizon)

        st.subheader(f"{product_choice} Demand Forecast")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=result.history["ds"],
            y=result.history["y"],
            name="Historical",
            mode="lines"
        ))
        fig.add_trace(go.Scatter(
            x=result.forecast["ds"],
            y=result.forecast["y"],
            name="Forecast",
            mode="lines",
            line=dict(dash="dash")
        ))
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "Use this forecast to optimize inventory and prevent stock-outs."
        )

# ==================================================
# 3️⃣ CUSTOMER REVENUE RISK FORECAST
# ==================================================
elif forecast_mode == "Customer Revenue Risk Forecast":

    customer_cols = [c for c in categorical_cols if "customer" in c.lower()]

    if not customer_cols:
        st.warning("No customer column detected.")
    else:
        customer_col = customer_cols[0]

        customer_perf = (
            df.groupby(customer_col)[metric_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        st.subheader("Top 10 Customer Revenue Projection")

        risk_analysis = []

        for cust in customer_perf.index:
            cust_df = df[df[customer_col] == cust]

            ts = ForecastEngine.prepare_time_series(
                df=cust_df,
                date_col=date_col,
                target_col=metric_col,
                freq=freq
            )

            result = ForecastEngine.forecast(ts=ts, periods=horizon)

            last_actual = result.history["y"].iloc[-1]
            forecast_value = result.forecast["y"].iloc[-1]
            growth_pct = ((forecast_value / last_actual) - 1) * 100

            risk_level = "Low"
            if growth_pct < -10:
                risk_level = "High"
            elif growth_pct < 0:
                risk_level = "Moderate"

            risk_analysis.append({
                "Customer": cust,
                "Projected Change (%)": round(growth_pct, 1),
                "Risk Level": risk_level
            })

        risk_df = pd.DataFrame(risk_analysis)
        st.dataframe(risk_df, use_container_width=True)

        st.info(
            "High-risk customers may require retention strategy or engagement campaigns."
        )

# --------------------------------------------------
# NEXT
# --------------------------------------------------
st.divider()

next_col, spacer = st.columns([1, 4])

with next_col:
    if st.button("Next", use_container_width=True):
        st.switch_page("pages/5_Report_Studio.py")

st.caption("InsightX · Multi-Level Forecasting Engine")
