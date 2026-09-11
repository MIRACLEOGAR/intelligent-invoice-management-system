"""
src/customer_id_generator.py

Automatic customer ID generation.
"""

from src.customer_engine import (
    load_customers
)


# ==================================
# GENERATE CUSTOMER ID
# ==================================

def generate_customer_id():

    customers = load_customers()

    if customers.empty:

        return "CUST-0001"

    customer_ids = customers[
        "customer_id"
    ].astype(str)

    last_id = customer_ids.iloc[-1]

    number = int(

        last_id.replace(
            "CUST-",
            ""
        )

    )

    return f"CUST-{number + 1:04d}"