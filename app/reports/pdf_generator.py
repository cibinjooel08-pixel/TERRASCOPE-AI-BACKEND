import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any

class PDFReportGenerator:
    """
    Generates professional Earth Observation PDF Reports.
    """

    def generate_pdf_report(self, analysis_data: Dict[str, Any]) -> bytes:
        """
        Builds a full PDF report buffer from analysis JSON data.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold"
        )

        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0284c7"),
            fontName="Helvetica"
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold",
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        bold_label = ParagraphStyle(
            "BoldLabel",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0f172a")
        )

        elements = []

        # Header Title
        elements.append(Paragraph("SATQUERY AI — EARTH OBSERVATION REPORT", title_style))
        elements.append(Paragraph("Ask the Earth. Understand the Change. | Powered by Copernicus CDSE", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=15))

        # Query & Summary Block
        query_text = analysis_data.get("query", "Earth Surface Change Query")
        specialist = analysis_data.get("specialist", "Bi-Temporal Specialist")
        conclusion = analysis_data.get("conclusion", "Surface change detected.")

        summary_data = [
            [Paragraph("Natural Query:", bold_label), Paragraph(query_text, body_style)],
            [Paragraph("Specialist Pipeline:", bold_label), Paragraph(specialist, body_style)],
            [Paragraph("Executive Conclusion:", bold_label), Paragraph(f"<b>{conclusion}</b>", body_style)],
        ]

        t_summary = Table(summary_data, colWidths=[120, 420])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 12))

        # Key Metrics Table
        elements.append(Paragraph("Key Analysis Metrics", heading_style))
        change_metrics = analysis_data.get("change_metrics", {})
        conf_info = analysis_data.get("confidence", {})

        metrics_table_data = [
            ["Metric", "Value", "Notes / Description"],
            ["Change Percentage", f"{change_metrics.get('change_percentage', 0.0)}%", "Percentage of AOI pixels with spectral/SAR shift"],
            ["Affected Area", f"{change_metrics.get('affected_area_sq_km', 0.0)} sq km", "Estimated physical surface change extent"],
            ["SatQuery Change Score", f"{change_metrics.get('earth_change_score', 0.0)} / 100", "Normalized Earth Change Index indicator"],
            ["Overall Confidence", f"{conf_info.get('overall_confidence_pct', 0.0)}% ({conf_info.get('rating', 'HIGH')})", f"Data Reliability: {conf_info.get('data_reliability_badge', 'Good')}"],
        ]

        t_metrics = Table(metrics_table_data, colWidths=[140, 140, 260])
        t_metrics.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ]))
        elements.append(t_metrics)
        elements.append(Spacer(1, 12))

        # Provenance Block
        elements.append(Paragraph("Data Provenance & Audit Trail", heading_style))
        prov = analysis_data.get("provenance", {})

        prov_data = [
            ["Data Source", prov.get("data_provider", "Copernicus Data Space Ecosystem")],
            ["Satellite & Collection", f"{prov.get('primary_satellite', 'SENTINEL-2')} ({prov.get('collection', 'L2A')})"],
            ["Acquisition Date A", f"Requested: {prov.get('requested_date_a')} | Actual: {prov.get('actual_date_a')}"],
            ["Acquisition Date B", f"Requested: {prov.get('requested_date_b')} | Actual: {prov.get('actual_date_b')}"],
            ["Cloud Coverage", f"Date A: {prov.get('cloud_coverage_a', 0.0)}% | Date B: {prov.get('cloud_coverage_b', 0.0)}%"],
            ["AOI Coordinates", str(prov.get("aoi_bounding_box", []))],
        ]

        t_prov = Table(prov_data, colWidths=[150, 390])
        t_prov.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(t_prov)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = PDFReportGenerator()
