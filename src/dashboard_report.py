"""
src/dashboard_report.py
Generates a full visual PDF report of the Dashboard Analytics page,
embedding Plotly chart images (via kaleido) and a KPI summary table.

Requires: pip install kaleido
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from src.paths import REPORTS_DIR

NAVY = colors.HexColor("#1B2A4A")
TEAL = colors.HexColor("#2E8B8B")
LIGHT_GREY = colors.HexColor("#F2F2F2")


def _format_currency(value):
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    return f"${value:,.0f}"


def generate_dashboard_pdf(kpis, charts, recent_invoices):
    """
    kpis: dict of KPI values (see keys used below)
    charts: dict of {chart_title: plotly_figure}
    recent_invoices: pandas DataFrame (subset of columns to display)

    Returns the file path of the generated PDF.
    """

    os.makedirs(REPORTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(
        REPORTS_DIR, f"Dashboard_Report_{timestamp}.pdf"
    )

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()
    story = []

    # =========================
    # TITLE
    # =========================
    title_style = ParagraphStyle(
        "title", fontSize=18, fontName="Helvetica-Bold",
        textColor=NAVY, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "subtitle", fontSize=10, fontName="Helvetica",
        textColor=colors.grey, spaceAfter=14
    )

    story.append(Paragraph("Smart Invoice System — Dashboard Report", title_style))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        subtitle_style
    ))

    # =========================
    # KPI SUMMARY TABLE
    # =========================
    section_style = ParagraphStyle(
        "section", fontSize=13, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=6, spaceAfter=8
    )
    story.append(Paragraph("Key Performance Indicators", section_style))

    kpi_rows = [
        ["Registered Customers", str(kpis.get("registered_customers", 0)),
         "Purchasing Customers", str(kpis.get("purchasing_customers", 0))],
        ["Total Invoices", str(kpis.get("total_invoices", 0)),
         "Paid Invoices", str(kpis.get("paid_invoices", 0))],
        ["Total Revenue", _format_currency(kpis.get("total_revenue", 0)),
         "Amount Collected", _format_currency(kpis.get("amount_collected", 0))],
        ["Collection Rate", f"{kpis.get('collection_rate', 0):.1f}%",
         "Outstanding Balance", _format_currency(kpis.get("outstanding_balance", 0))],
        ["Avg Invoice Value", _format_currency(kpis.get("avg_invoice_value", 0)),
         "Overdue Invoices", str(kpis.get("overdue_invoices", 0))],
        ["New Customers (This Month)", str(kpis.get("new_customers_this_month", 0)),
         "", ""],
    ]

    kpi_table = Table(
        kpi_rows,
        colWidths=[5.5 * cm, 3 * cm, 5.5 * cm, 3 * cm]
    )
    kpi_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (1, 0), (1, -1), TEAL),
        ("TEXTCOLOR", (3, 0), (3, -1), TEAL),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(kpi_table)
    story.append(Spacer(1, 0.6 * cm))

    # =========================
    # CHARTS (embedded as images via kaleido)
    # =========================
    story.append(Paragraph("Visual Analytics", section_style))

    chart_img_width = 16.5 * cm
    chart_img_height = 8.5 * cm

    for chart_title, fig in charts.items():

        try:
            img_bytes = fig.to_image(format="png", width=1100, height=560, scale=2)
        except Exception as e:
            # kaleido not installed or export failed — skip this chart gracefully
            story.append(Paragraph(
                f"<i>Could not render chart '{chart_title}': {e}</i>",
                styles["Normal"]
            ))
            continue

        img_path = os.path.join(
            REPORTS_DIR, f"_tmp_{chart_title.replace(' ', '_')}_{timestamp}.png"
        )
        with open(img_path, "wb") as f:
            f.write(img_bytes)

        chart_label_style = ParagraphStyle(
            "chart_label", fontSize=11, fontName="Helvetica-Bold",
            textColor=colors.HexColor("#333333"), spaceBefore=10, spaceAfter=4
        )
        story.append(Paragraph(chart_title, chart_label_style))
        story.append(Image(img_path, width=chart_img_width, height=chart_img_height))
        story.append(Spacer(1, 0.3 * cm))

    # =========================
    # RECENT INVOICES TABLE
    # =========================
    story.append(PageBreak())
    story.append(Paragraph("Recent Invoices", section_style))

    if recent_invoices is not None and not recent_invoices.empty:

        table_data = [list(recent_invoices.columns)]

        for _, row in recent_invoices.iterrows():
            formatted_row = []
            for col, val in zip(recent_invoices.columns, row):
                if col == "total_amount":
                    formatted_row.append(f"${val:,.2f}")
                elif col == "invoice_date":
                    formatted_row.append(str(val)[:10])
                else:
                    formatted_row.append(str(val))
            table_data.append(formatted_row)

        n_cols = len(recent_invoices.columns)
        col_width = (17.5 * cm) / n_cols

        invoices_table = Table(table_data, colWidths=[col_width] * n_cols)
        invoices_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(invoices_table)

    else:
        story.append(Paragraph("No recent invoices to display.", styles["Normal"]))

    # =========================
    # FOOTER
    # =========================
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "Generated by MiracleAnalytics Smart Invoice System",
        ParagraphStyle("footer", fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)

    # Clean up temp chart images
    for chart_title in charts.keys():
        img_path = os.path.join(
            REPORTS_DIR, f"_tmp_{chart_title.replace(' ', '_')}_{timestamp}.png"
        )
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
            except Exception:
                pass

    return output_path