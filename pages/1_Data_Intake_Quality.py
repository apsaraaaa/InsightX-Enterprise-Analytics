import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.eda_engine import EDAEngine

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="InsightX | Data Intake",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "quality_report" not in st.session_state:
    st.session_state.quality_report = None

if "eda_summary" not in st.session_state:
    st.session_state.eda_summary = None

if "data_locked" not in st.session_state:
    st.session_state.data_locked = False

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("Data Intake & Profiling")
st.caption(
    "Upload your dataset and perform early-stage validation, profiling, "
    "and readiness assessment before deeper analysis."
)

st.divider()

# --------------------------------------------------
# DATA UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload dataset (CSV, Excel, Parquet)",
    type=["csv", "xlsx", "xls", "parquet"]
)

if uploaded_file:
    with st.spinner("Loading and validating dataset..."):
        df = DataLoader.load_dataset(uploaded_file)
        quality = DataCleaner.generate_quality_report(df)
        eda = EDAEngine.run(df)

        st.session_state.df = df
        st.session_state.quality_report = quality
        st.session_state.eda_summary = eda
        st.session_state.data_locked = True

# --------------------------------------------------
# STOP IF NO DATA
# --------------------------------------------------
if st.session_state.df is None:
    st.info("Upload a dataset to begin analysis.")
    st.stop()

df = st.session_state.df
quality = st.session_state.quality_report

rows, cols = df.shape

numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

# --------------------------------------------------
# STEP 1: DATASET OVERVIEW
# --------------------------------------------------
st.divider()
st.subheader("Step 1: Dataset Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{rows:,}")
c2.metric("Columns", cols)
c3.metric("Numeric Columns", len(numeric_cols))
c4.metric("Categorical Columns", len(categorical_cols))

# --------------------------------------------------
# STEP 2: DATA PREVIEW
# --------------------------------------------------
st.divider()
st.subheader("Step 2: Data Preview")

st.dataframe(df.head(10), use_container_width=True, height=350)

# --------------------------------------------------
# STEP 3: DATA QUALITY SUMMARY
# --------------------------------------------------
st.divider()
st.subheader("Step 3: Data Quality Summary")

q1, q2, q3, q4, q5 = st.columns(5)
q1.metric("Missing Cells", f"{quality.missing_cells:,}")
q2.metric("Missing %", f"{quality.missing_pct}%")
q3.metric("Duplicate Rows", f"{quality.duplicate_rows:,}")
q4.metric("Outliers", f"{quality.outlier_cells:,}")
q5.metric("Quality Score", f"{quality.quality_score}/100")

# --------------------------------------------------
# STEP 4: DATA PROFILING & STRUCTURE
# --------------------------------------------------
st.divider()
st.subheader("Step 4: Data Profiling & Structure")

identifier_cols = [
    c for c in df.columns if df[c].nunique() / len(df) > 0.9
]

c1, c2, c3 = st.columns(3)
c1.metric("Numeric Features", len(numeric_cols))
c2.metric("Categorical Features", len(categorical_cols))
c3.metric("Potential Identifier Columns", len(identifier_cols))

st.caption(
    "Structural profiling helps identify feature types, identifiers, "
    "and overall dataset composition early in the analysis lifecycle."
)

# --------------------------------------------------
# STEP 5: FEATURE PROFILING SUMMARY
# --------------------------------------------------
st.divider()
st.subheader("Step 5: Feature Profiling Summary")

if numeric_cols:
    profile_df = pd.DataFrame({
        "Feature": numeric_cols,
        "Mean": df[numeric_cols].mean().round(2),
        "Std Dev": df[numeric_cols].std().round(2),
        "Min": df[numeric_cols].min(),
        "Max": df[numeric_cols].max(),
        "Missing %": (df[numeric_cols].isna().mean() * 100).round(1)
    })

    st.dataframe(profile_df, use_container_width=True, height=300)
else:
    st.info("No numeric features available for profiling.")

# --------------------------------------------------
# STEP 6: INTEGRITY & MISSINGNESS SIGNALS
# --------------------------------------------------
st.divider()
st.subheader("Step 6: Integrity & Missingness Signals")

missing_pct = (
    df.isna()
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

critical_missing = missing_pct[missing_pct > 20]

if not critical_missing.empty:
    st.markdown("Columns with significant missingness (>20%):")
    for col, pct in critical_missing.items():
        st.markdown(f"- `{col}`: {pct:.1f}% missing")
else:
    st.markdown("No columns with critical missingness detected.")

st.caption(
    "High missingness can reduce analytical reliability and "
    "should be addressed before advanced modeling."
)

# --------------------------------------------------
# STEP 7: RELATIONSHIP & REDUNDANCY SIGNALS
# --------------------------------------------------
st.divider()
st.subheader("Step 7: Relationship & Redundancy Signals")

if len(numeric_cols) >= 2:
    corr = df[numeric_cols].corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

    redundant_pairs = [
        (a, b, upper.loc[a, b])
        for a in upper.index
        for b in upper.columns
        if upper.loc[a, b] > 0.85
    ]

    if redundant_pairs:
        st.markdown("Highly correlated numeric feature pairs:")
        for a, b, val in redundant_pairs:
            st.markdown(f"- `{a}` and `{b}` (correlation: {val:.2f})")
    else:
        st.markdown("No highly correlated numeric feature pairs detected.")
else:
    st.info("Insufficient numeric features for correlation analysis.")

# --------------------------------------------------
# STEP 8: ANALYSIS READINESS SUMMARY
# --------------------------------------------------
st.divider()
st.subheader("Step 8: Analysis Readiness Summary")

readiness = {
    "Regression Analysis": len(numeric_cols) >= 2,
    "Classification Analysis": any(df[c].nunique() == 2 for c in df.columns),
    "Time Series Analysis": any(
        "date" in c.lower() or "time" in c.lower() for c in df.columns
    ),
    "Requires Data Cleaning": df.isna().any().any()
}

for item, status in readiness.items():
    st.markdown(f"- **{item}**: {'Yes' if status else 'No'}")

st.caption(
    "Readiness indicators are heuristic and intended to guide next steps, "
    "not prescribe analytical outcomes."
)

# --------------------------------------------------
# NEXT BUTTON
# --------------------------------------------------
st.divider()

left, _, _ = st.columns([1, 6, 1])

with left:
    if st.button("Next", use_container_width=True):
        st.switch_page("pages/2_Dashboards.py")
