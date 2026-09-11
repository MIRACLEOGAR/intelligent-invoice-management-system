"""
src/payment_engine.py
Records payments against invoices, updates invoice balances, logs payment
history (including customer name and payment method for reporting/activity
feeds), and refreshes the invoice PDF.
"""

import os
import pandas as pd

from datetime import datetime

from src.payment_id_engine import (
    generate_payment_id
)

from src.paths import (
    PROCESSED_INVOICES_FILE,
    PAYMENT_LOG_FILE
)

from src.pdf_refresh_engine import (
    refresh_invoice_pdf
)


def record_payment(
    invoice_id,
    payment_amount,
    payment_method="Not Specified"
):

    # =========================
    # LOAD INVOICE DATA
    # =========================

    invoices_df = pd.read_excel(
        PROCESSED_INVOICES_FILE
    )

    invoice_rows = invoices_df[
        invoices_df["invoice_id"]
        == invoice_id
    ]

    if invoice_rows.empty:

        raise ValueError(
            f"Invoice not found: {invoice_id}"
        )

    # =========================
    # CURRENT VALUES
    # =========================

    current_paid = float(
        invoice_rows[
            "amount_paid"
        ].iloc[0]
    )

    total_invoice_amount = float(
        invoice_rows[
            "total_amount"
        ].sum()
    )

    customer_name = (
        invoice_rows["customer"].iloc[0]
        if "customer" in invoice_rows.columns
        else "Unknown"
    )

    # =========================
    # NEW BALANCES
    # =========================

    new_amount_paid = (
        current_paid
        + payment_amount
    )

    if new_amount_paid > total_invoice_amount:

        raise ValueError(
            "Payment exceeds remaining balance."
        )

    balance_due = (
        total_invoice_amount
        - new_amount_paid
    )

    # =========================
    # PAYMENT STATUS
    # =========================

    if balance_due <= 0:

        payment_status = "PAID"

    elif new_amount_paid > 0:

        payment_status = (
            "PARTIALLY PAID"
        )

    else:

        payment_status = (
            "UNPAID"
        )

    # =========================
    # UPDATE ALL INVOICE ROWS
    # =========================

    mask = (
        invoices_df["invoice_id"]
        == invoice_id
    )

    invoices_df.loc[
        mask,
        "amount_paid"
    ] = new_amount_paid

    invoices_df.loc[
        mask,
        "balance_due"
    ] = balance_due

    invoices_df.loc[
        mask,
        "payment_status"
    ] = payment_status

    invoices_df.to_excel(
        PROCESSED_INVOICES_FILE,
        index=False
    )

    # =========================
    # LOG PAYMENT
    # =========================

    payment_id = (
        generate_payment_id()
    )

    payment_record = {

        "payment_id":
            payment_id,

        "invoice_id":
            invoice_id,

        "customer":
            customer_name,

        "amount_paid":
            payment_amount,

        "payment_method":
            payment_method,

        "payment_date":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "status_after_payment":
            payment_status

    }

    if os.path.exists(
        PAYMENT_LOG_FILE
    ):

        payment_log = pd.read_excel(
            PAYMENT_LOG_FILE
        )

        payment_log = pd.concat(
            [
                payment_log,
                pd.DataFrame(
                    [payment_record]
                )
            ],
            ignore_index=True
        )

    else:

        payment_log = pd.DataFrame(
            [payment_record]
        )

    payment_log.to_excel(
        PAYMENT_LOG_FILE,
        index=False
    )

    # =========================
    # REFRESH PDF
    # =========================

    refresh_invoice_pdf(
        invoice_id
    )

    # =========================
    # RETURN RESULTS
    # =========================

    return {

        "payment_id":
            payment_id,

        "invoice_id":
            invoice_id,

        "customer":
            customer_name,

        "total_amount":
            total_invoice_amount,

        "amount_paid":
            new_amount_paid,

        "balance_due":
            balance_due,

        "payment_status":
            payment_status

    }


def get_recent_payments(limit=5):
    """
    Returns the most recent payment log entries, newest first.
    Used by the Home page's Recent Payments / Recent Activity views.
    """

    if not os.path.exists(PAYMENT_LOG_FILE):
        return pd.DataFrame(columns=[
            "payment_id", "invoice_id", "customer",
            "amount_paid", "payment_method",
            "payment_date", "status_after_payment"
        ])

    payment_log = pd.read_excel(PAYMENT_LOG_FILE)

    if payment_log.empty:
        return payment_log

    payment_log["payment_date"] = pd.to_datetime(
        payment_log["payment_date"]
    )

    return (
        payment_log
        .sort_values("payment_date", ascending=False)
        .head(limit)
    )
print("PAYMENT ENGINE LOADED")

print(
    "AVAILABLE FUNCTIONS:",
    [name for name in globals().keys() if not name.startswith("_")]
)

