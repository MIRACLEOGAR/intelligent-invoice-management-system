"""
src/pdf_generator.py
Invoice PDF generator for Smart_Invoice_System
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from textwrap import wrap

from src.config import (
    COMPANY_NAME,
    COMPANY_TAGLINE,
    COMPANY_ADDRESS,
    COMPANY_EMAIL,
    COMPANY_PHONE,
    CURRENCY_SYMBOL,
    CURRENCY_CODE,
)
from src.paths import LOGO_PATH

# =========================
# LAYOUT-SPECIFIC COLORS
# =========================
NAVY = colors.HexColor("#1B2A4A")
TEAL = colors.HexColor("#2E8B8B")

# Default payment term if no due_date is supplied
DEFAULT_PAYMENT_TERM_DAYS = 14


# ══════════════════════════════════════════════════════════════════════
# HELPER — normalize any date-like value (str, datetime, pd.Timestamp)
# into a "YYYY-MM-DD" string
# ══════════════════════════════════════════════════════════════════════
def _to_date_str(value):
    """Convert a string, datetime, or pandas Timestamp into 'YYYY-MM-DD'."""
    if isinstance(value, str):
        return pd.to_datetime(value).strftime("%Y-%m-%d")
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def _to_datetime_obj(value):
    """Convert a string, datetime, or pandas Timestamp into a python datetime."""
    if isinstance(value, str):
        return pd.to_datetime(value).to_pydatetime()
    return pd.Timestamp(value).to_pydatetime()


# ══════════════════════════════════════════════════════════════════════
# PDF GENERATOR
# ══════════════════════════════════════════════════════════════════════
def generate_invoice_pdf(invoice_data, output_path, logo_path=LOGO_PATH):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 50
    right_edge = width - margin

    # =========================
    # HEADER BAND (NAVY) WITH TEAL WAVE
    # =========================
    header_height = 140

    c.setFillColor(NAVY)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)

    c.setFillColor(TEAL)
    p = c.beginPath()
    p.moveTo(0, height - header_height)
    p.curveTo(width * 0.25, height - header_height + 35,
              width * 0.55, height - header_height - 25,
              width, height - header_height + 15)
    p.lineTo(width, height - header_height)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # =========================
    # LOGO (ENLARGED, LEFT)
    # =========================
    if logo_path and os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, margin, height - 112, width=95, height=95,
                         mask='auto', preserveAspectRatio=True)
            text_x = margin + 105
        except Exception:
            text_x = margin
    else:
        text_x = margin

    # =========================
    # COMPANY INFO (HEADER, WHITE TEXT)
    # =========================
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(text_x, height - 50, COMPANY_NAME)

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(text_x, height - 65, COMPANY_TAGLINE)

    c.setFont("Helvetica", 8)
    c.drawString(text_x, height - 80, COMPANY_ADDRESS)
    c.drawString(text_x, height - 92, f"{COMPANY_EMAIL}  |  {COMPANY_PHONE}")

    # =========================
    # INVOICE TITLE (RIGHT, IN HEADER)
    # =========================
    c.setFont("Helvetica-Bold", 28)
    c.drawRightString(right_edge, height - 50, "INVOICE")

    # =========================
    # INVOICE TO / META INFO (just below header)
    # =========================
    c.setFillColor(colors.black)
    y = height - header_height - 35

    # ── Normalize invoice_date (handles str, datetime, pd.Timestamp) ──
    invoice_date_str = _to_date_str(invoice_data["invoice_date"])

    # ── Calculate / normalize due_date ──
    due_date_raw = invoice_data.get("due_date")
    if due_date_raw:
        due_date = _to_date_str(due_date_raw)
    else:
        invoice_date_obj = _to_datetime_obj(invoice_data["invoice_date"])
        due_date = (invoice_date_obj + timedelta(days=DEFAULT_PAYMENT_TERM_DAYS)).strftime("%Y-%m-%d")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Invoice To:")
    c.setFont("Helvetica", 9)
    c.drawString(margin, y - 14, invoice_data['customer'])
    c.drawString(margin, y - 28, f"Order ID: {invoice_data.get('order_id', 'N/A')}")
    c.drawString(margin, y - 42, f"Due Date: {due_date}")

    # ── Customer contact details (optional fields) ──
    contact_y = y - 56
    contact_fields = [
        ("Phone",   invoice_data.get("phone", "")),
        ("Email",   invoice_data.get("email", "")),
        ("Address", invoice_data.get("address", "")),
        ("City",    invoice_data.get("city", "")),
        ("Country", invoice_data.get("country", "")),
    ]

    for label, value in contact_fields:
        if value:
            c.drawString(margin, contact_y, f"{label}: {value}")
            contact_y -= 14

    # Right side meta
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(right_edge, y, f"Invoice No: {invoice_data['invoice_id']}")
    c.setFont("Helvetica", 9)
    c.drawRightString(right_edge, y - 14, f"Issue Date: {invoice_date_str}")

    # =========================
    # ITEMS TABLE
    # =========================
    # table_top adjusts dynamically based on how many contact lines were drawn
    table_top = min(contact_y - 20, y - 75)
    col_x = {
        "no": margin,
        "desc": margin + 50,
        "qty": margin + 300,
        "price": margin + 380,
    }
    row_height = 22

    LIGHT_GREY = colors.HexColor("#F2F2F2")
    DARK_GREY = colors.HexColor("#333333")

    # Table header row (navy background)
    c.setFillColor(NAVY)
    c.rect(margin, table_top - row_height, right_edge - margin, row_height, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(col_x["no"] + 5, table_top - row_height + 7, "Item No")
    c.drawString(col_x["desc"] + 5, table_top - row_height + 7, "Description")
    c.drawString(col_x["qty"] + 5, table_top - row_height + 7, "Qty")
    c.drawString(col_x["price"] + 5, table_top - row_height + 7, "Price")

    # Items rows (alternating shading)
    c.setFont("Helvetica", 9)
    y_row = table_top - row_height
    subtotal = 0

    for idx, item in enumerate(invoice_data["items"], start=1):
        total = item["quantity"] * item["unit_price"]
        subtotal += total
        y_row -= row_height

        if idx % 2 == 0:
            c.setFillColor(LIGHT_GREY)
            c.rect(margin, y_row, right_edge - margin, row_height, fill=1, stroke=0)

        c.setFillColor(DARK_GREY)
        c.drawString(col_x["no"] + 5, y_row + 7, f"{idx:02d}")
        c.drawString(col_x["desc"] + 5, y_row + 7, item['product'])
        c.drawString(col_x["qty"] + 5, y_row + 7, f"{item['quantity']:02d}")
        c.drawString(col_x["price"] + 5, y_row + 7, f"{CURRENCY_SYMBOL}{item['unit_price']:.2f}")

    # Table border
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.setLineWidth(0.5)
    c.rect(margin, y_row, right_edge - margin, table_top - y_row, fill=0, stroke=1)
    for col in [col_x["desc"], col_x["qty"], col_x["price"]]:
        c.line(col, y_row, col, table_top)

    # =========================
    # TOTALS SECTION
    # =========================
    tax_rate = invoice_data.get("tax_rate", 0.20)
    vat = subtotal * tax_rate
    total = subtotal + vat

    totals_x = col_x["qty"]
    totals_width = right_edge - totals_x
    totals_y = y_row - 30

    # Subtotal row
    c.setFillColor(LIGHT_GREY)
    c.rect(totals_x, totals_y, totals_width, row_height, fill=1, stroke=0)
    c.setFillColor(DARK_GREY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(totals_x + 5, totals_y + 7, "Sub Total:")
    c.setFont("Helvetica", 9)
    c.drawRightString(right_edge - 5, totals_y + 7, f"{CURRENCY_SYMBOL}{subtotal:.2f}")

    # Tax row
    totals_y -= row_height
    c.setFillColor(colors.white)
    c.rect(totals_x, totals_y, totals_width, row_height, fill=1, stroke=1)
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.setFillColor(DARK_GREY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(totals_x + 5, totals_y + 7, f"Tax ({tax_rate*100:.0f}%):")
    c.setFont("Helvetica", 9)
    c.drawRightString(right_edge - 5, totals_y + 7, f"{CURRENCY_SYMBOL}{vat:.2f}")

    # Grand Total → TOTAL DUE row (visible but not solid-highlighted)
    totals_y -= row_height
    c.setFillColor(colors.white)
    c.rect(totals_x, totals_y, totals_width, row_height, fill=1, stroke=1)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(totals_x + 5, totals_y + 7, "TOTAL DUE:")
    c.drawRightString(right_edge - 5, totals_y + 7, f"{CURRENCY_SYMBOL}{total:.2f}")
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.HexColor("#CCCCCC"))

    # =========================
    # PAYMENT SUMMARY SECTION
    # =========================
    amount_paid = invoice_data.get("amount_paid", 0)
    balance_due = invoice_data.get("balance_due", total)
    payment_status = invoice_data.get("payment_status", "UNPAID")

    # Small gap + section label
    totals_y -= 18
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(totals_x + 5, totals_y + 4, "Payment Summary")

    # Amount Paid row
    totals_y -= row_height
    c.setFillColor(LIGHT_GREY)
    c.rect(totals_x, totals_y, totals_width, row_height, fill=1, stroke=0)
    c.setFillColor(DARK_GREY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(totals_x + 5, totals_y + 7, "Amount Paid:")
    c.setFont("Helvetica", 9)
    c.drawRightString(right_edge - 5, totals_y + 7, f"{CURRENCY_SYMBOL}{amount_paid:.2f}")

    # Balance Due row
    totals_y -= row_height
    c.setFillColor(colors.white)
    c.rect(totals_x, totals_y, totals_width, row_height, fill=1, stroke=1)
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.setFillColor(DARK_GREY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(totals_x + 5, totals_y + 7, "Balance Due:")
    c.setFont("Helvetica", 9)
    c.drawRightString(right_edge - 5, totals_y + 7, f"{CURRENCY_SYMBOL}{balance_due:.2f}")

    # Status row — plain background, status shown via icon + colored text
    status_upper = str(payment_status).upper()
    if status_upper == "PAID":
        status_color = colors.HexColor("#1E8449")    # green
    elif status_upper == "PARTIALLY PAID":
        status_color = colors.HexColor("#B7950B")    # amber
    else:
        status_color = colors.HexColor("#B03A2E")    # red

    totals_y -= row_height
    c.setFillColor(LIGHT_GREY)
    c.rect(totals_x, totals_y, totals_width, row_height, fill=1, stroke=0)

    c.setFillColor(DARK_GREY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(totals_x + 5, totals_y + 7, "Status:")

    # Status indicator: checkmark for PAID, filled circle otherwise
    indicator_radius = 4
    text_right_x = right_edge - 5
    c.setFont("Helvetica-Bold", 9)
    status_text_width = c.stringWidth(status_upper, "Helvetica-Bold", 9)
    circle_cx = text_right_x - status_text_width - 10
    circle_cy = totals_y + 9

    if status_upper == "PAID":
        # Draw a small checkmark instead of a circle
        c.setStrokeColor(status_color)
        c.setLineWidth(1.6)
        c.line(circle_cx - 4, circle_cy, circle_cx - 1, circle_cy - 3)
        c.line(circle_cx - 1, circle_cy - 3, circle_cx + 4, circle_cy + 4)
        c.setLineWidth(0.5)
    else:
        c.setFillColor(status_color)
        c.circle(circle_cx, circle_cy, indicator_radius, fill=1, stroke=0)

    c.setFillColor(status_color)
    c.drawRightString(text_right_x, totals_y + 7, status_upper)

    # =========================
    # TERMS AND CONDITIONS (LEFT, ALONGSIDE TOTALS)
    # =========================
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, totals_y + row_height + 30, "Terms And Conditions:")
    c.setFont("Helvetica", 7)
    terms_text = invoice_data.get("terms",
        f"Payment is due within {DEFAULT_PAYMENT_TERM_DAYS} days of the invoice date. "
        "Late payments may be subject to additional fees.")

    wrapped = wrap(terms_text, 55)
    ty = totals_y + row_height + 15
    for line in wrapped[:4]:
        c.drawString(margin, ty, line)
        ty -= 10

    # =========================
    # FOOTER LINE
    # =========================
    c.setFillColor(colors.grey)
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 40,
                         "Generated by MiracleAnalytics Invoice Management System")

    c.save()