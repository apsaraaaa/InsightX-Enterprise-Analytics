# pages/5_Report_Studio.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

st.set_page_config(page_title="InsightX | Universal Enterprise Report", layout="wide")

st.title("Universal Enterprise Executive Report")
st.caption("Fully Data-Agnostic Strategic Intelligence Engine")

# --------------------------------------------------
# DATA CHECK
# --------------------------------------------------
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("Complete analysis first.")
    st.stop()

df = st.session_state.df.copy()

numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

if not numeric_cols:
    st.error("Dataset must contain at least one numeric column.")
    st.stop()

# Primary metric selection logic
primary_metric = df[numeric_cols].std().idxmax()

total_value = df[primary_metric].sum()
record_count = len(df)
avg_value = df[primary_metric].mean()
std_dev = df[primary_metric].std()
volatility_ratio = std_dev / avg_value if avg_value else 0

forecast_growth = st.session_state.get("forecast_growth", None)

# Detect date columns dynamically
date_cols = []
for col in df.columns:
    try:
        converted = pd.to_datetime(df[col], errors="coerce")
        if converted.notna().sum() > 0.6 * len(df):
            date_cols.append(col)
    except:
        pass

# Detect binary classification column
binary_cols = [c for c in df.columns if df[c].nunique() == 2]

# --------------------------------------------------
# COVER INPUT
# --------------------------------------------------
st.subheader("Cover Page")

report_title = st.text_input("Report Title", "INSIGHTX ENTERPRISE ANALYTICS REPORT")
company_name = st.text_input("Company Name", "Confidential Organization")
prepared_by = st.text_input("Prepared By", "Analytics Team")

st.divider()

# --------------------------------------------------
# PDF GENERATOR
# --------------------------------------------------
def generate_pdf():

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    H1 = styles["Heading1"]
    normal = styles["Normal"]

    # -----------------------------
    # KPI DETECTION
    # -----------------------------
    exclude_keywords = ["id", "month", "year", "date", "number"]
    candidate_cols = [
        col for col in numeric_cols
        if not any(k in col.lower() for k in exclude_keywords)
    ]
    kpi_col = candidate_cols[0] if candidate_cols else numeric_cols[0]

    # -----------------------------
    # CORE METRICS
    # -----------------------------
    total = df[kpi_col].sum()
    mean = df[kpi_col].mean()
    median = df[kpi_col].median()
    std = df[kpi_col].std()
    min_val = df[kpi_col].min()
    max_val = df[kpi_col].max()
    skewness = df[kpi_col].skew()
    kurtosis = df[kpi_col].kurt()
    volatility_ratio = std / mean if mean != 0 else 0

    missing_percent = (df.isna().sum().sum() / (df.shape[0]*df.shape[1])) * 100

    # -----------------------------
    # COVER PAGE
    # -----------------------------
    elements.append(Paragraph(report_title, H1))
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(f"Prepared For: {company_name}", normal))
    elements.append(Paragraph(f"Prepared By: {prepared_by}", normal))
    elements.append(Paragraph(f"Date: {datetime.today().strftime('%d %B %Y')}", normal))
    elements.append(PageBreak())

    # -----------------------------
    # PAGE 2 — EXECUTIVE SUMMARY
    # -----------------------------
    elements.append(Paragraph("1. Executive Summary", H1))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"Primary KPI: {kpi_col}", normal))
    elements.append(Spacer(1, 0.2 * inch))

    summary_points = [
        f"1. Total KPI Value: {total:,.2f}",
        f"2. Average KPI: {mean:,.2f}",
        f"3. Median KPI: {median:,.2f}",
        f"4. Volatility Ratio: {volatility_ratio:.2f}",
        f"5. Missing Data: {missing_percent:.2f}%",
        "6. Performance dispersion indicates operational variability."
    ]

    for point in summary_points:
        elements.append(Paragraph(point, normal))
        elements.append(Spacer(1, 0.15 * inch))

    elements.append(PageBreak())

    # -----------------------------
    # PAGE 3 — KPI STATISTICS + DISTRIBUTION
    # -----------------------------
    elements.append(Paragraph("2. KPI Statistical Diagnostics", H1))
    elements.append(Spacer(1, 0.3 * inch))

    stats_data = [
        ["Metric", "Value"],
        ["Total", f"{total:,.2f}"],
        ["Mean", f"{mean:,.2f}"],
        ["Median", f"{median:,.2f}"],
        ["Std Dev", f"{std:,.2f}"],
        ["Min", f"{min_val:,.2f}"],
        ["Max", f"{max_val:,.2f}"],
        ["Skewness", f"{skewness:.2f}"],
        ["Kurtosis", f"{kurtosis:.2f}"]
    ]

    table = Table(stats_data, colWidths=[2.5*inch, 2.5*inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    plt.figure(figsize=(6,3))
    df[kpi_col].hist(bins=30)
    plt.title(f"{kpi_col} Distribution")
    plt.tight_layout()
    img = BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)

    elements.append(Image(img, width=6*inch, height=3*inch))
    elements.append(PageBreak())

    # -----------------------------
    # PAGE 4 — SEGMENT ANALYSIS
    # -----------------------------
    if categorical_cols:
        cat = categorical_cols[0]
        contribution = df.groupby(cat)[kpi_col].sum().sort_values(ascending=False)

        elements.append(Paragraph("3. Segment Contribution Analysis", H1))
        elements.append(Spacer(1, 0.3 * inch))

        seg_data = [["Segment", "Contribution"]]
        for idx, val in contribution.head(5).items():
            seg_data.append([str(idx), f"{val:,.2f}"])

        seg_table = Table(seg_data, colWidths=[2.5*inch, 2.5*inch])
        seg_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ]))

        elements.append(seg_table)
        elements.append(Spacer(1, 0.3 * inch))

        plt.figure(figsize=(6,3))
        contribution.head(10).plot(kind="bar")
        plt.title("Top Contributors")
        plt.tight_layout()
        img = BytesIO()
        plt.savefig(img, format="png")
        plt.close()
        img.seek(0)

        elements.append(Image(img, width=6*inch, height=3*inch))
        elements.append(PageBreak())

    # -----------------------------
    # PAGE 5 — CORRELATION
    # -----------------------------
    if len(numeric_cols) > 1:
        elements.append(Paragraph("4. Correlation Analysis", H1))
        elements.append(Spacer(1, 0.3 * inch))

        corr = df[numeric_cols].corr()

        plt.figure(figsize=(6,4))
        sns.heatmap(corr, cmap="coolwarm")
        plt.title("Correlation Heatmap")
        plt.tight_layout()
        img = BytesIO()
        plt.savefig(img, format="png")
        plt.close()
        img.seek(0)

        elements.append(Image(img, width=6*inch, height=4*inch))

        elements.append(Spacer(1, 0.3 * inch))

        corr_points = [
            "1. Strong correlations (>0.7) indicate predictive linkage.",
            "2. Negative correlation suggests inverse relationship.",
            "3. Multicollinearity may impact regression models.",
            "4. Independent variables improve modeling strength.",
            "5. Correlation does not imply causation.",
            "6. Further statistical testing recommended."
        ]

        for point in corr_points:
            elements.append(Paragraph(point, normal))
            elements.append(Spacer(1, 0.15 * inch))

        elements.append(PageBreak())

    # -----------------------------
    # PAGE 6 — STRATEGIC RECOMMENDATIONS
    # -----------------------------
    elements.append(Paragraph("5. Strategic Recommendations", H1))
    elements.append(Spacer(1, 0.3 * inch))

    strategy_points = [
        "1. Monitor KPI volatility monthly.",
        "2. Reduce high segment dependency.",
        "3. Deploy predictive forecasting models.",
        "4. Implement anomaly detection framework.",
        "5. Strengthen data governance protocols.",
        "6. Develop executive dashboard reporting."
    ]

    for point in strategy_points:
        elements.append(Paragraph(point, normal))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("Generate Universal Enterprise Report"):
    pdf = generate_pdf()
    st.download_button(
        "Download Enterprise PDF",
        data=pdf,
        file_name="InsightX_Enterprise_Report.pdf",
        mime="application/pdf"
    )