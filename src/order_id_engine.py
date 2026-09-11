"""
src/order_id_engine.py

Generates sequential order IDs.

Format:
ORD-2026-0001
ORD-2026-0002
ORD-2026-0003
"""

import json
import os
from datetime import datetime

from src.paths import DATA_DIR

COUNTER_FILE = os.path.join(
    DATA_DIR,
    "order_counter.json"
)


def generate_order_id():

    current_year = datetime.now().year

    key = str(current_year)

    if os.path.exists(COUNTER_FILE):

        with open(
            COUNTER_FILE,
            "r"
        ) as f:

            data = json.load(f)

    else:

        data = {}

    current_count = data.get(key, 0) + 1

    data[key] = current_count

    with open(
        COUNTER_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

    return (
        f"ORD-{current_year}-"
        f"{current_count:04d}"
    )