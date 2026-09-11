import pandas as pd
import random
import os

from datetime import datetime, timedelta

from src.paths import (
    INVOICE_INPUT_FILE,
    PRODUCT_MASTER_FILE,
    CUSTOMER_MASTER_FILE,
    PROCESSED_INVOICES_FILE,
    ensure_directories,
)

ensure_directories()

# ============================
# READ FILES
# ============================

invoice_df = pd.read_excel(
    INVOICE_INPUT_FILE
)

product_df = pd.read_excel(
    PRODUCT_MASTER_FILE
)

customer_df = pd.read_excel(
    CUSTOMER_MASTER_FILE
)

# ============================
# MERGE PRODUCT DATA
# ============================

merged_df = invoice_df.merge(
    product_df,
    on="product",
    how="left"
)

# ============================
# MERGE CUSTOMER DATA
# ============================

merged_df = merged_df.merge(
    customer_df,
    left_on="customer",
    right_on="customer_name",
    how="left"
)

# ============================
# GENERATE HISTORICAL TIMESTAMPS
# ============================

today = datetime.today()

start_date = today - timedelta(days=730)

timestamps = []

for _ in range(len(merged_df)):

    random_days = random.randint(0, 730)

    random_hours = random.randint(8, 18)

    random_minutes = random.randint(0, 59)

    timestamp = start_date + timedelta(
        days=random_days,
        hours=random_hours,
        minutes=random_minutes
    )

    timestamps.append(timestamp)

merged_df["timestamp"] = timestamps

# ============================
# SORT BY TIMESTAMP
# ============================

merged_df = merged_df.sort_values(
    by="timestamp"
).reset_index(drop=True)

# ============================
# HISTORICAL INVOICE IDS
# ============================

merged_df["invoice_id"] = [

    f"HIST-{i:05d}"

    for i in range(
        1,
        len(merged_df) + 1
    )
]

# ============================
# GENERATE ORDER IDS
# ============================

order_ids = []

current_order = 1

row_index = 0

while row_index < len(merged_df):

    group_size = random.randint(1, 8)

    order_id = (
        f"ORD-{today.year}-{current_order:04d}"
    )

    for _ in range(group_size):

        if row_index >= len(merged_df):
            break

        order_ids.append(order_id)

        row_index += 1

    current_order += 1

merged_df["order_id"] = order_ids

# ============================
# DATES
# ============================

merged_df["invoice_date"] = (
    merged_df["timestamp"].dt.date
)

merged_df["due_date"] = (
    pd.to_datetime(
        merged_df["invoice_date"]
    )
    + timedelta(days=14)
)

# ============================
# CALCULATIONS
# ============================

merged_df["subtotal"] = (
    merged_df["quantity"]
    * merged_df["unit_price"]
)

merged_df["vat_amount"] = (
    merged_df["subtotal"]
    * merged_df["vat_rate"]
    / 100
)

merged_df["total_amount"] = (
    merged_df["subtotal"]
    + merged_df["vat_amount"]
)

# ============================
# PAYMENT TRACKING
# ============================

merged_df["amount_paid"] = 0

merged_df["balance_due"] = (
    merged_df["total_amount"]
)

merged_df["payment_status"] = (
    merged_df["payment_status"]
    .astype(str)
    .str.upper()
)

# ============================
# FORMAT OUTPUT
# ============================

merged_df["timestamp"] = (
    merged_df["timestamp"]
    .dt.strftime("%Y-%m-%d %H:%M:%S")
)

merged_df["invoice_date"] = (
    pd.to_datetime(
        merged_df["invoice_date"]
    )
    .dt.strftime("%Y-%m-%d")
)

merged_df["due_date"] = (
    pd.to_datetime(
        merged_df["due_date"]
    )
    .dt.strftime("%Y-%m-%d")
)

# ============================
# FINAL STRUCTURE
# ============================

final_columns = [

    "invoice_id",

    "order_id",

    "timestamp",

    "invoice_date",

    "due_date",

    "customer_id",

    "customer",

    "phone",

    "email",

    "address",

    "city",

    "country",

    "product",

    "category",

    "quantity",

    "unit_price",

    "subtotal",

    "vat_rate",

    "vat_amount",

    "total_amount",

    "amount_paid",

    "balance_due",

    "payment_status"

]

processed_df = merged_df[
    final_columns
]

# ============================
# SAVE FILE
# ============================

try:

    if os.path.exists(
        PROCESSED_INVOICES_FILE
    ):
        os.remove(
            PROCESSED_INVOICES_FILE
        )

except PermissionError:

    print(
        "❌ Close processed_invoices.xlsx before running."
    )

    raise

processed_df.to_excel(
    PROCESSED_INVOICES_FILE,
    index=False
)

# ============================
# SUMMARY
# ============================

print(
    "\n✅ Processed invoice file generated successfully!"
)

print(
    f"📄 Total Rows: {len(processed_df)}"
)

print(
    f"📦 Total Orders: {processed_df['order_id'].nunique()}"
)

print(
    f"📁 Saved to: {PROCESSED_INVOICES_FILE}"
)