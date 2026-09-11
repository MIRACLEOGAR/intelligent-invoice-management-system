"""
src/pdf_refresh_engine.py

Rebuilds an invoice PDF from the latest
processed_invoices.xlsx data.

Before refreshing an existing invoice PDF,
the previous version is archived so that
invoice history can be preserved.

Used whenever:
- Invoice is created/refreshed
- Payment is recorded
- Invoice is updated
"""

import os
import shutil
from datetime import datetime

import pandas as pd

from src.paths import (
    PROCESSED_INVOICES_FILE,
    REPORTS_DIR
)

from src.pdf_generator import (
    generate_invoice_pdf
)


# ==================================================
# ARCHIVE EXISTING PDF
# ==================================================

def archive_existing_invoice_pdf(
    invoice_id,
    customer
):
    """
    Archives the current invoice PDF before it is
    replaced by an updated version.
    """

    current_pdf_path = os.path.join(
        REPORTS_DIR,
        f"{invoice_id}_{str(customer).replace(' ', '_')}.pdf"
    )

    if not os.path.exists(current_pdf_path):
        return None

    history_dir = os.path.join(
        REPORTS_DIR,
        "invoice_history",
        str(invoice_id)
    )

    os.makedirs(
        history_dir,
        exist_ok=True
    )

    existing_versions = [
        filename
        for filename in os.listdir(history_dir)
        if filename.lower().endswith(".pdf")
    ]

    version_number = len(existing_versions) + 1

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    customer_safe = (
        str(customer)
        .replace(" ", "_")
    )

    archive_filename = (
        f"{invoice_id}_v{version_number}_"
        f"{timestamp}_{customer_safe}.pdf"
    )

    archive_path = os.path.join(
        history_dir,
        archive_filename
    )

    shutil.copy2(
        current_pdf_path,
        archive_path
    )

    return archive_path


# ==================================================
# REFRESH INVOICE PDF
# ==================================================

def refresh_invoice_pdf(invoice_id):

    # =========================
    # LOAD DATA
    # =========================

    df = pd.read_excel(
        PROCESSED_INVOICES_FILE
    )

    invoice_rows = df[
        df["invoice_id"] == invoice_id
    ]

    if invoice_rows.empty:

        raise ValueError(
            f"Invoice not found: {invoice_id}"
        )

    # =========================
    # HEADER DETAILS
    # =========================

    first_row = invoice_rows.iloc[0]

    customer = first_row["customer"]

    invoice_date = first_row["invoice_date"]

    due_date = first_row["due_date"]

    order_id = first_row["order_id"]

    amount_paid = float(
        first_row["amount_paid"]
    )

    balance_due = float(
        first_row["balance_due"]
    )

    payment_status = str(
        first_row["payment_status"]
    )

    phone = first_row.get(
        "phone",
        ""
    )

    email = first_row.get(
        "email",
        ""
    )

    address = first_row.get(
        "address",
        ""
    )

    city = first_row.get(
        "city",
        ""
    )

    country = first_row.get(
        "country",
        ""
    )

    # =========================
    # ARCHIVE CURRENT PDF
    # =========================

    archive_existing_invoice_pdf(
        invoice_id,
        customer
    )

    # =========================
    # BUILD PDF ITEMS
    # =========================

    pdf_items = []

    for _, row in invoice_rows.iterrows():

        pdf_items.append({

            "product":
                row["product"],

            "quantity":
                int(row["quantity"]),

            "unit_price":
                float(row["unit_price"])

        })

    # =========================
    # TAX RATE
    # =========================

    tax_rate = float(
        first_row["vat_rate"]
    ) / 100

    # =========================
    # BUILD PDF DATA
    # =========================

    invoice_data = {

        "invoice_id":
            invoice_id,

        "order_id":
            order_id,

        "invoice_date":
            invoice_date,

        "due_date":
            due_date,

        "customer":
            customer,

        "phone":
            phone,

        "email":
            email,

        "address":
            address,

        "city":
            city,

        "country":
            country,

        "items":
            pdf_items,

        "tax_rate":
            tax_rate,

        "amount_paid":
            amount_paid,

        "balance_due":
            balance_due,

        "payment_status":
            payment_status

    }

    # =========================
    # PDF PATH
    # =========================

    output_path = os.path.join(

        REPORTS_DIR,

        f"{invoice_id}_{str(customer).replace(' ', '_')}.pdf"

    )

    # =========================
    # GENERATE UPDATED PDF
    # =========================

    generate_invoice_pdf(

        invoice_data,

        output_path

    )

    return output_path