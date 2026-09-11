"""
src/invoice_number_engine.py
Generates sequential invoice numbers (e.g. INV-2026-06-0001),
persisting the running count per month in invoice_counter.json
"""

import json
import os
from datetime import datetime

from src.paths import INVOICE_COUNTER_FILE


def generate_invoice_number():
    now = datetime.now()
    key = f"{now.year}-{str(now.month).zfill(2)}"

    if os.path.exists(INVOICE_COUNTER_FILE):
        with open(INVOICE_COUNTER_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    count = data.get(key, 0) + 1
    data[key] = count

    with open(INVOICE_COUNTER_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return f"INV-{now.year}-{str(now.month).zfill(2)}-{str(count).zfill(4)}"