"""
src/customer_engine.py

Customer data operations for Smart Invoice System.
"""

import pandas as pd

from src.paths import (
    CUSTOMER_MASTER_FILE
)

CUSTOMER_FILE = CUSTOMER_MASTER_FILE

# ==================================
# LOAD CUSTOMERS
# ==================================

def load_customers():

    try:

        customers = pd.read_excel(
            CUSTOMER_MASTER_FILE
        )

        if "status" not in customers.columns:

            customers["status"] = "ACTIVE"

        return customers

    except FileNotFoundError:

        return pd.DataFrame(columns=[

            "customer_id",

            "customer_name",

            "phone",

            "email",

            "address",

            "city",

            "country",

            "status"

        ])


# ==================================
# SAVE CUSTOMERS
# ==================================

def save_customers(df):

    df.to_excel(

        CUSTOMER_MASTER_FILE,

        index=False

    )


# ==================================
# ADD CUSTOMER
# ==================================

def add_customer(customer_data):

    customers = load_customers()

    if "status" not in customer_data:

        customer_data["status"] = "ACTIVE"

    customers = pd.concat(

        [
            customers,
            pd.DataFrame([customer_data])
        ],

        ignore_index=True

    )

    save_customers(customers)


# ==================================
# GET ACTIVE CUSTOMER NAMES
# ==================================

def get_customer_names():

    customers = load_customers()

    active_customers = customers[

        customers["status"]
        .astype(str)
        .str.upper()
        ==
        "ACTIVE"

    ]

    return active_customers[
        "customer_name"
    ].tolist()


# ==================================
# GET ALL CUSTOMER NAMES
# ==================================

def get_all_customer_names():

    customers = load_customers()

    return customers[
        "customer_name"
    ].tolist()


# ==================================
# GET CUSTOMER DETAILS
# ==================================

def get_customer_details(
    customer_name
):

    customers = load_customers()

    result = customers[

        customers["customer_name"]
        ==
        customer_name

    ]

    if result.empty:

        return None

    return result.iloc[0]


# ==================================
# SEARCH CUSTOMERS
# ==================================

def search_customers(
    keyword
):

    customers = load_customers()

    result = customers[

        customers["customer_name"]
        .astype(str)
        .str.contains(

            str(keyword),

            case=False,

            na=False

        )

    ]

    return result


# ==================================
# CUSTOMER EXISTS
# ==================================

def customer_exists(
    customer_name
):

    customers = load_customers()

    return (

        customer_name

        in

        customers[
            "customer_name"
        ]
        .astype(str)
        .values

    )


# ==================================
# UPDATE CUSTOMER
# ==================================

def update_customer(

    customer_id,

    updated_data

):

    customers = load_customers()

    mask = (

        customers["customer_id"]
        ==
        customer_id

    )

    customers.loc[
        mask,
        "customer_name"
    ] = updated_data[
        "customer_name"
    ]

    customers.loc[
        mask,
        "phone"
    ] = updated_data[
        "phone"
    ]

    customers.loc[
        mask,
        "email"
    ] = updated_data[
        "email"
    ]

    customers.loc[
        mask,
        "address"
    ] = updated_data[
        "address"
    ]

    customers.loc[
        mask,
        "city"
    ] = updated_data[
        "city"
    ]

    customers.loc[
        mask,
        "country"
    ] = updated_data[
        "country"
    ]

    save_customers(
        customers
    )


# ==================================
# UPDATE CUSTOMER STATUS
# ==================================

def update_customer_status(

    customer_id,

    status

):

    customers = load_customers()

    mask = (

        customers["customer_id"]
        ==
        customer_id

    )

    if mask.sum() == 0:

        return (

            False,

            "Customer not found."

        )

    customers.loc[
        mask,
        "status"
    ] = status.upper()

    save_customers(
        customers
    )

    return (

        True,

        f"Customer marked as {status.upper()}."

    )