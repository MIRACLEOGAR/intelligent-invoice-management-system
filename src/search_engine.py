import pandas as pd

from src.paths import (
    PROCESSED_INVOICES_FILE
)


def load_invoices():

    return pd.read_excel(
        PROCESSED_INVOICES_FILE
    )


# ==================================
# SEARCH FUNCTIONS
# ==================================

def search_by_invoice_id(invoice_id):

    df = load_invoices()

    return df[
        df["invoice_id"]
        .astype(str)
        .str.upper()
        ==
        invoice_id.upper()
    ]


def search_by_customer(customer):

    df = load_invoices()

    return df[
        df["customer"]
        .astype(str)
        .str.contains(
            customer,
            case=False,
            na=False
        )
    ]


def search_by_order_id(order_id):

    df = load_invoices()

    return df[
        df["order_id"]
        .astype(str)
        .str.upper()
        ==
        order_id.upper()
    ]


def search_by_status(status):

    df = load_invoices()

    return df[
        df["payment_status"]
        .astype(str)
        .str.upper()
        ==
        status.upper()
    ]


# ==================================
# PAYMENT TRACKING SUPPORT
# ==================================

def get_invoice_summary(invoice_id):

    df = load_invoices()

    invoice_rows = df[

        df["invoice_id"]
        .astype(str)
        .str.upper()
        ==
        invoice_id.upper()

    ]

    if invoice_rows.empty:

        return None

    first_row = invoice_rows.iloc[0]

    return {

        "invoice_id":
            first_row["invoice_id"],

        "customer":
            first_row["customer"],

        "invoice_total":
            float(
                invoice_rows[
                    "total_amount"
                ].sum()
            ),

        "amount_paid":
            float(
                first_row[
                    "amount_paid"
                ]
            ),

        "balance_due":
            float(
                first_row[
                    "balance_due"
                ]
            ),

        "payment_status":
            first_row[
                "payment_status"
            ]

    }