from fpdf import FPDF
from pathlib import Path
from datetime import datetime


class ExecutivePDF(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "InsightX Executive Analytics Report", ln=True)
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=9)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


class ReportGenerator:

    @staticmethod
    def generate_pdf_report(
        *,
        df,
        quality_report,
        eda_summary,
        insights,
        dataset_name,
        author,
        output_dir: Path = Path("outputs/reports")
    ) -> Path:

        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / "InsightX_Executive_Report.pdf"

        pdf = ExecutivePDF()
        pdf.set_auto_page_break(auto=True, margin=20)

        # -------------------------------
        # COVER PAGE
        # -------------------------------
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 15, "InsightX Executive Analytics Report", ln=True)

        pdf.ln(10)
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"Dataset: {dataset_name}", ln=True)
        pdf.cell(0, 10, f"Author: {author}", ln=True)
        pdf.cell(0, 10, datetime.now().strftime("%B %Y"), ln=True)

        # -------------------------------
        # DATASET OVERVIEW
        # -------------------------------
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Dataset Overview", ln=True)

        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(
            0, 8,
            f"The dataset contains {df.shape[0]:,} records "
            f"and {df.shape[1]} variables. "
            "It has been evaluated for structure, quality, and analytical readiness."
        )

        pdf.ln(5)
        pdf.multi_cell(
            0, 8,
            f"Data Confidence Level: {quality_report.confidence_level}\n"
            f"Quality Score: {quality_report.quality_score}/100\n"
            f"Missing Percentage: {quality_report.missing_pct}%\n"
            f"Duplicate Rows: {quality_report.duplicate_rows}"
        )

        # -------------------------------
        # DATA QUALITY
        # -------------------------------
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Data Quality Assessment", ln=True)

        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(
            0, 8,
            "The dataset quality was assessed across completeness, duplication, "
            "and outlier presence to ensure reliable analytics and decision support."
        )

        pdf.ln(4)
        pdf.multi_cell(
            0, 8,
            f"Missing Cells: {quality_report.missing_cells}\n"
            f"Outlier Cells: {quality_report.outlier_cells}\n"
            f"Duplicate Rows: {quality_report.duplicate_rows}"
        )

        # -------------------------------
        # DECISION INSIGHTS
        # -------------------------------
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Key Decision Insights", ln=True)

        pdf.set_font("Helvetica", size=11)

        if insights:
            for idx, ins in enumerate(insights, start=1):
                pdf.multi_cell(
                    0, 8,
                    f"{idx}. {ins.get('title', 'Insight')}\n"
                    f"{ins.get('description', '')}\n"
                    f"Impact: {ins.get('impact', '')}"
                )
                pdf.ln(2)
        else:
            pdf.multi_cell(
                0, 8,
                "No high-impact insights were generated for this dataset."
            )

        # -------------------------------
        # RECOMMENDATIONS
        # -------------------------------
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Strategic Recommendations", ln=True)

        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(
            0, 8,
            "Based on the analytical findings, the following actions are recommended:\n"
            "- Promote stable metrics as KPIs\n"
            "- Monitor high-variance drivers\n"
            "- Use forecasting for planning\n"
            "- Apply scenario modeling for risk evaluation"
        )

        # -------------------------------
        # SAVE
        # -------------------------------
        pdf.output(str(pdf_path))
        return pdf_path
