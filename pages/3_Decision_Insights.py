# pages/3_Decision_Insights.py

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="InsightX | Executive Decision Intelligence",
    layout="wide"
)

st.title("Executive Decision Intelligence")
st.caption("Strategic Intelligence Layer derived from structural, categorical, and temporal signals.")

st.divider()

# --------------------------------------------------
# DATA CHECK
# --------------------------------------------------
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("Please upload dataset first.")
    st.stop()

df = st.session_state.df.copy()

numeric_cols = df.select_dtypes(include="number").columns.tolist()

if not numeric_cols:
    st.error("Numeric columns required.")
    st.stop()

# --------------------------------------------------
# PRIMARY BUSINESS METRIC DETECTION
# --------------------------------------------------
primary_metric = df[numeric_cols].sum().idxmax()

total_value = df[primary_metric].sum()
record_count = len(df)
avg_value = df[primary_metric].mean()
std_dev = df[primary_metric].std()
volatility_ratio = std_dev / avg_value if avg_value != 0 else 0

# --------------------------------------------------
# INTELLIGENT COLUMN DETECTION
# --------------------------------------------------
product_cols = [c for c in df.columns if any(x in c.lower() for x in ["product", "line", "category"])]
country_cols = [c for c in df.columns if any(x in c.lower() for x in ["country", "region", "market"])]
customer_cols = [c for c in df.columns if any(x in c.lower() for x in ["customer", "client", "name"])]
status_cols = [c for c in df.columns if "status" in c.lower()]
date_cols = [c for c in df.columns if "date" in c.lower()]

st.header("Page 1: Executive Snapshot")

c1, c2, c3 = st.columns(3)
c1.metric("Total Records", f"{record_count:,}")
c2.metric("Total Value", f"{total_value:,.2f}")
c3.metric("Average Value", f"{avg_value:,.2f}")

st.markdown(f"""
The dataset contains **{record_count:,} records**, generating a total value of **{total_value:,.2f}**.  
The average contribution per record is **{avg_value:,.2f}**, with a standard deviation of **{std_dev:,.2f}**, indicating the degree of structural variability across transactions.

The calculated volatility ratio of **{volatility_ratio:.2f}** suggests that the revenue structure is **{'highly variable' if volatility_ratio > 1 else 'moderately stable' if volatility_ratio > 0.5 else 'structurally stable'}**.
""")

st.divider()

# --------------------------------------------------
# PRODUCT / CATEGORY INTELLIGENCE
# --------------------------------------------------
if product_cols:
    product_col = product_cols[0]
    product_perf = df.groupby(product_col)[primary_metric].sum().sort_values(ascending=False)

    top_product = product_perf.index[0]
    top_share = product_perf.iloc[0] / total_value * 100

    st.header("Page 2: Product & Category Intelligence")

    st.markdown(f"""
Analysis of product performance reveals that **{top_product}** is the strongest revenue contributor, accounting for approximately **{top_share:.1f}%** of total value.

The revenue distribution across product lines suggests **{'moderate concentration risk' if top_share > 40 else 'a diversified product structure with limited dependency exposure'}**.

Strategic Implication:
Scaling high-performing categories while optimizing underperforming segments can enhance margin performance and reduce structural dependency risk.
""")

    st.divider()

# --------------------------------------------------
# GEOGRAPHIC INTELLIGENCE
# --------------------------------------------------
if country_cols:
    country_col = country_cols[0]
    geo_perf = df.groupby(country_col)[primary_metric].sum().sort_values(ascending=False)

    top_market = geo_perf.index[0]
    geo_share = geo_perf.iloc[0] / total_value * 100

    st.header("Page 3: Geographic & Market Intelligence")

    st.markdown(f"""
Geographic analysis indicates that **{top_market}** represents the dominant revenue driver, contributing approximately **{geo_share:.1f}%** of total value.

This suggests **{'geographic concentration exposure' if geo_share > 50 else 'a balanced regional distribution with moderate dependency'}**.

Strategic Implication:
Diversifying revenue streams across secondary markets may reduce dependency risk and support sustainable expansion.
""")

    st.divider()

# --------------------------------------------------
# TEMPORAL & SEASONAL INTELLIGENCE
# --------------------------------------------------
if date_cols:
    date_col = date_cols[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["Year"] = df[date_col].dt.year

    yearly = df.groupby("Year")[primary_metric].sum()
    peak_year = yearly.idxmax()

    st.header("Page 4: Seasonality & Trend Intelligence")

    st.markdown(f"""
Temporal analysis reveals structured revenue movement over time.  
The strongest annual performance was observed in **{peak_year}**, indicating a peak growth phase during that period.

Recent trends suggest **{'continued expansion momentum' if yearly.iloc[-1] > yearly.mean() else 'performance stabilization or normalization'}**.

Strategic Implication:
Aligning marketing, inventory planning, and capacity management with observed seasonal cycles can improve operational efficiency.
""")

    st.divider()

# --------------------------------------------------
# CUSTOMER DEPENDENCY ANALYSIS
# --------------------------------------------------
if customer_cols:
    customer_col = customer_cols[0]
    customer_perf = df.groupby(customer_col)[primary_metric].sum().sort_values(ascending=False)

    top10_share = customer_perf.head(10).sum() / total_value * 100

    st.header("Page 5: Structural Risk & Dependency")

    st.markdown(f"""
The top 10 contributors account for approximately **{top10_share:.1f}%** of total revenue.

This indicates **{'high dependency risk on limited customers' if top10_share > 60 else 'a healthy diversification across the customer base'}**.

Strategic Implication:
Retention programs for high-value customers and expansion of mid-tier accounts can stabilize long-term revenue streams.
""")

    st.divider()

# --------------------------------------------------
# STRATEGIC SYNTHESIS
# --------------------------------------------------
st.header("Page 6: Strategic Intelligence Synthesis")

recommendations = []

if volatility_ratio > 1:
    recommendations.append("Prioritize volatility stabilization before aggressive expansion.")
else:
    recommendations.append("Leverage structural stability to pursue controlled growth strategies.")

if product_cols:
    recommendations.append("Scale high-performing product categories while optimizing low-margin segments.")

if country_cols:
    recommendations.append("Diversify geographic revenue sources to reduce regional concentration exposure.")

if customer_cols:
    recommendations.append("Strengthen retention strategies for high-value customer segments.")

if date_cols:
    recommendations.append("Synchronize marketing and supply planning with seasonal demand cycles.")

st.markdown("Integrated strategic recommendations based on combined intelligence signals:")

for rec in recommendations:
    st.markdown(f"- {rec}")

st.divider()

# --------------------------------------------------
# STORE SUMMARY FOR REPORT
# --------------------------------------------------
st.session_state.decision_summary = {
    "total_value": total_value,
    "avg_value": avg_value,
    "volatility_ratio": volatility_ratio,
}

# --------------------------------------------------
# NEXT
# --------------------------------------------------
next_col, spacer = st.columns([1, 4])

with next_col:
    if st.button("Next", use_container_width=True):
        st.switch_page("pages/4_Forecasting.py")
