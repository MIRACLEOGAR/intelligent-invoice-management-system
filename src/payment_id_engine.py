"""
src/payment_id_engine.py

Generates sequential payment IDs.

Example:

PAY-000001
PAY-000002
PAY-000003
"""

import json
import os

from src.paths import (
    PAYMENT_COUNTER_FILE
)


def generate_payment_id():

    if not os.path.exists(
        PAYMENT_COUNTER_FILE
    ):

        with open(
            PAYMENT_COUNTER_FILE,
            "w"
        ) as f:

            json.dump(
                {"counter": 0},
                f,
                indent=4
            )

    with open(
        PAYMENT_COUNTER_FILE,
        "r"
    ) as f:

        data = json.load(f)

    counter = (
        data["counter"] + 1
    )

    data["counter"] = counter

    with open(
        PAYMENT_COUNTER_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

    return f"PAY-{counter:06d}"