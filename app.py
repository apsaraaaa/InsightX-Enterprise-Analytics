import streamlit as st

# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="InsightX | Enterprise Analytics Platform",
    layout="wide",
    initial_sidebar_state="expanded"
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

if "selected_metric" not in st.session_state:
    st.session_state.selected_metric = None

if "forecast_output" not in st.session_state:
    st.session_state.forecast_output = None

if "forecast_growth" not in st.session_state:
    st.session_state.forecast_growth = None

if "forecast_metric" not in st.session_state:
    st.session_state.forecast_metric = None

if "forecast_horizon" not in st.session_state:
    st.session_state.forecast_horizon = None

# --------------------------------------------------
# HOME PAGE CONTENT
# --------------------------------------------------
st.title("InsightX")
st.subheader("Enterprise Analytics & Forecasting Intelligence Platform")

st.markdown("""
InsightX is an integrated analytical system designed to transform raw datasets into:

- Structured Data Profiling
- Interactive Dashboard Intelligence
- Executive-Level Decision Insights
- Forecasting & Scenario Analysis
- Automated Strategic Reporting

This platform follows a full analytical lifecycle:

1. Data Intake & Quality Validation  
2. Dashboard-Based Exploratory Intelligence  
3. Strategic Decision Insight Generation  
4. Time-Series Forecasting & Risk Modeling  
5. Automated Executive Report Generation  

Use the sidebar to navigate through the analytical workflow.
""")

st.divider()

# --------------------------------------------------
# WORKFLOW STATUS
# --------------------------------------------------
st.subheader("System Status")

col1, col2, col3 = st.columns(3)

if st.session_state.df is not None:
    col1.success("Dataset Loaded")
else:
    col1.warning("No Dataset Uploaded")

if st.session_state.data_locked:
    col2.success("Data Validated")
else:
    col2.warning("Data Not Validated")

if st.session_state.forecast_output is not None:
    col3.success("Forecast Generated")
else:
    col3.info("Forecast Not Generated")

st.divider()

st.caption("InsightX · End-to-End Business Intelligence Architecture")
