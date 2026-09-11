"""
src/live_invoice_engine.py

Creates a live invoice from multiple products,
saves invoice records into processed_invoices.xlsx,
and generates a PDF invoice.
"""

import os
import pandas as pd

from datetime import datetime, timedelta

from src.invoice_number_engine import (
    generate_invoice_number
)

from src.order_id_engine import (
    generate_order_id
)

from src.pdf_generator import (
    generate_invoice_pdf
)

from src.paths import (
    PROCESSED_INVOICES_FILE,
    PRODUCT_MASTER_FILE,
    REPORTS_DIR
)


def create_live_invoice(
    customer_details,
    items
):

    # =========================
    # LOAD PRODUCT MASTER
    # =========================

    products_df = pd.read_excel(
        PRODUCT_MASTER_FILE
    )

    # =========================
    # INVOICE DETAILS
    # =========================

    invoice_id = generate_invoice_number()

    order_id = generate_order_id()

    now = datetime.now()

    due_date = (
        now + timedelta(days=14)
    )

    # =========================
    # CUSTOMER DETAILS
    # =========================

    customer_id = customer_details[
        "customer_id"
    ]

    customer_name = customer_details[
        "customer_name"
    ]

    phone = customer_details[
        "phone"
    ]

    email = customer_details[
        "email"
    ]

    address = customer_details[
        "address"
    ]

    city = customer_details[
        "city"
    ]

    country = customer_details[
        "country"
    ]

    # =========================
    # BUILD INVOICE ROWS
    # =========================

    all_rows = []

    pdf_items = []

    vat_rates = []

    for item in items:

        product = item["product"]

        quantity = item["quantity"]

        product_row = products_df[
            products_df["product"]
            == product
        ]

        if product_row.empty:

            raise ValueError(
                f"Product not found: {product}"
            )

        unit_price = float(
            product_row[
                "unit_price"
            ].iloc[0]
        )

        vat_rate = float(
            product_row[
                "vat_rate"
            ].iloc[0]
        )

        category = product_row[
            "category"
        ].iloc[0]

        subtotal = (
            quantity * unit_price
        )

        vat_amount = (
            subtotal * vat_rate / 100
        )

        total_amount = (
            subtotal + vat_amount
        )

        vat_rates.append(
            vat_rate
        )

        row = {

            "invoice_id":
                invoice_id,

            "order_id":
                order_id,

            "timestamp":
                now.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "invoice_date":
                now.strftime(
                    "%Y-%m-%d"
                ),

            "due_date":
                due_date.strftime(
                    "%Y-%m-%d"
                ),

            "customer_id":
                customer_id,

            "customer":
                customer_name,

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

            "product":
                product,

            "category":
                category,

            "quantity":
                quantity,

            "unit_price":
                unit_price,

            "subtotal":
                subtotal,

            "vat_rate":
                vat_rate,

            "vat_amount":
                vat_amount,

            "total_amount":
                total_amount,

            # Invoice-level fields
            # will be updated later

            "amount_paid":
                0,

            "balance_due":
                0,

            "payment_status":
                "UNPAID"
        }

        all_rows.append(
            row
        )

        pdf_items.append({

            "product":
                product,

            "quantity":
                quantity,

            "unit_price":
                unit_price

        })

    # =========================
    # CREATE DATAFRAME
    # =========================

    new_df = pd.DataFrame(
        all_rows
    )

    # =========================
    # INVOICE LEVEL TOTALS
    # =========================

    invoice_total = round(

        float(
            new_df[
                "total_amount"
            ].sum()
        ),

        2

    )

    new_df[
        "amount_paid"
    ] = 0

    new_df[
        "balance_due"
    ] = invoice_total

    new_df[
        "payment_status"
    ] = "UNPAID"

    # =========================
    # SAVE TO DATASET
    # =========================

    if os.path.exists(
        PROCESSED_INVOICES_FILE
    ):

        existing_df = pd.read_excel(
            PROCESSED_INVOICES_FILE
        )

        final_df = pd.concat(

            [
                existing_df,
                new_df
            ],

            ignore_index=True

        )

    else:

        final_df = new_df

    final_df.to_excel(

        PROCESSED_INVOICES_FILE,

        index=False

    )

    # =========================
    # PDF PATH
    # =========================

    output_path = os.path.join(

        REPORTS_DIR,

        f"{invoice_id}_{customer_name.replace(' ', '_')}.pdf"

    )

    # =========================
    # PDF DATA
    # =========================

    invoice_data = {

        "order_id":
            order_id,

        "invoice_id":
            invoice_id,

        "invoice_date":
            now.strftime(
                "%Y-%m-%d"
            ),

        "due_date":
            due_date.strftime(
                "%Y-%m-%d"
            ),

        "customer":
            customer_name,

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
            (
                vat_rates[0] / 100
            )
            if vat_rates
            else 0,

        "amount_paid":
            0,

        "balance_due":
            invoice_total,

        "payment_status":
            "UNPAID"

    }

    # =========================
    # GENERATE PDF
    # =========================

    generate_invoice_pdf(

        invoice_data,

        output_path

    )

    # =========================
    # RETURN
    # =========================

    return (

        output_path,

        invoice_id

    )