"""
src/paths.py

Centralized path configuration for Smart_Invoice_System.

Every module should import paths from here
instead of rebuilding paths with os.path.dirname().

If the folder structure ever changes,
this is the only file that needs updating.
"""

import os

# =====================================================
# PROJECT ROOT
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# =====================================================
# CORE FOLDERS
# =====================================================

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

REPORTS_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

ASSETS_DIR = os.path.join(
    BASE_DIR,
    "assets"
)

# =====================================================
# HISTORICAL DATA FILES
# =====================================================

PROCESSED_INVOICES_FILE = os.path.join(
    DATA_DIR,
    "processed_invoices.xlsx"
)

PRODUCT_MASTER_FILE = os.path.join(
    DATA_DIR,
    "product_master_data.xlsx"
)

CUSTOMER_MASTER_FILE = os.path.join(
    DATA_DIR,
    "customer_master_data.xlsx"
)

INVOICE_INPUT_FILE = os.path.join(
    DATA_DIR,
    "invoice_input_data_300.xlsx"
)

TRANSACTION_LOG_FILE = os.path.join(
    DATA_DIR,
    "transactions_log.xlsx"
)

# =====================================================
# PAYMENT TRACKING FILES
# =====================================================

PAYMENT_LOG_FILE = os.path.join(
    DATA_DIR,
    "payment_log.xlsx"
)

# =====================================================
# COUNTER FILES
# =====================================================

INVOICE_COUNTER_FILE = os.path.join(
    DATA_DIR,
    "invoice_counter.json"
)

ORDER_COUNTER_FILE = os.path.join(
    DATA_DIR,
    "order_counter.json"
)

PAYMENT_COUNTER_FILE = os.path.join(
    DATA_DIR,
    "payment_counter.json"
)

# =====================================================
# ASSETS
# =====================================================

LOGO_PATH = os.path.join(
    ASSETS_DIR,
    "miracleanalytics_logo.png"
)

# =====================================================
# FUTURE DATABASE
# =====================================================

SQLITE_DB_FILE = os.path.join(
    DATA_DIR,
    "smart_invoice.db"
)

# =====================================================
# CREATE REQUIRED FOLDERS
# =====================================================

def ensure_directories():
    """
    Create required folders if they
    do not already exist.
    """

    folders = [

        DATA_DIR,

        REPORTS_DIR,

        ASSETS_DIR

    ]

    for folder in folders:

        os.makedirs(
            folder,
            exist_ok=True
        )