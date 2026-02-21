# pages/2_Dashboards.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="InsightX | Dashboards",
    layout="wide"
)

# --------------------------------------------------
# DATA CHECK
# --------------------------------------------------
if (
    "df" not in st.session_state
    or st.session_state.df is None
    or not st.session_state.data_locked
):
    st.warning("Please complete Data Intake first.")
    st.stop()

df = st.session_state.df.copy()
quality = st.session_state.quality_report

numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

if not numeric_cols:
    st.error("Numeric columns required.")
    st.stop()

# --------------------------------------------------
# FILTER SECTION
# --------------------------------------------------
st.subheader("Filters")

col1, col2 = st.columns(2)

with col1:
    metric_col = st.selectbox("Primary Metric", numeric_cols)

with col2:
    category_col = st.selectbox(
        "Category Column (Optional)",
        ["None"] + categorical_cols
    )

st.session_state.selected_metric = metric_col

# Apply category filter
if category_col != "None":
    values = st.multiselect(
        "Select Category Values",
        sorted(df[category_col].astype(str).unique())
    )
    if values:
        df = df[df[category_col].astype(str).isin(values)]

st.divider()

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("Key Performance Indicators")

total_value = df[metric_col].sum()
avg_value = df[metric_col].mean()
std_dev = df[metric_col].std()
record_count = len(df)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Value", f"{total_value:,.2f}")
k2.metric("Average Value", f"{avg_value:,.2f}")
k3.metric("Standard Deviation", f"{std_dev:,.2f}")
k4.metric("Records", f"{record_count:,}")

st.divider()

# --------------------------------------------------
# ROW 1 — TREND & CATEGORY
# --------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown("### Trend View")

    fig_line = px.line(
        df.reset_index(),
        x=df.reset_index().index,
        y=metric_col,
        template="plotly_dark"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.markdown("### Category Comparison")

    if category_col != "None":
        agg = (
            df.groupby(category_col)[metric_col]
            .sum()
            .reset_index()
        )

        fig_bar = px.bar(
            agg,
            x=category_col,
            y=metric_col,
            template="plotly_dark"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Select a category column to enable this chart.")

st.divider()

# --------------------------------------------------
# ROW 2 — DISTRIBUTION & OUTLIERS
# --------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.markdown("### Distribution")
    fig_hist = px.histogram(
        df,
        x=metric_col,
        nbins=30,
        template="plotly_dark"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with c4:
    st.markdown("### Outlier Analysis")
    fig_box = px.box(
        df,
        y=metric_col,
        template="plotly_dark"
    )
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()

# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------
st.subheader("Correlation Heatmap")

if len(numeric_cols) >= 2:
    corr = df[numeric_cols].corr()

    fig_corr = px.imshow(
        corr,
        text_auto=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.info("Not enough numeric features for correlation analysis.")

st.divider()

# --------------------------------------------------
# INTERPRETATION SECTION
# --------------------------------------------------
st.subheader("Analytical Interpretation")

st.markdown(f"""
• The dataset contains **{record_count:,} records**  
• Primary metric analyzed: **{metric_col}**  
• Distribution and outlier patterns indicate structural variability  
• Correlation heatmap highlights relationships between numeric features  
• These insights directly feed into Decision Intelligence and Forecasting  
""")

st.divider()

# --------------------------------------------------
# NEXT
# --------------------------------------------------
next_col, spacer = st.columns([1, 4])

with next_col:
    if st.button("Next", use_container_width=True):
        st.switch_page("pages/3_Decision_Insights.py")

st.caption("InsightX · Visual Analytics Layer")