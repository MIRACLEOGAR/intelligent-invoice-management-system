"""
src/customer_master_generator.py

Creates historical customer master data
for Smart Invoice System.
"""

import pandas as pd
import random

from src.paths import (
    CUSTOMER_MASTER_FILE
)

# =========================
# CUSTOMER NAMES
# =========================

customer_names = [

    "John Smith", "Emily Johnson", "Michael Brown",
    "Olivia Davis", "James Wilson", "Sophia Martinez",
    "Daniel Taylor", "Emma Anderson", "Liam Thomas",
    "Ava White", "Noah Harris", "Isabella Clark",
    "Oliver Lewis", "Mia Walker", "Elijah Hall",
    "Amelia Young", "William Scott", "Charlotte Adams",
    "Benjamin Carter", "Harper Mitchell", "Ethan Cooper",
    "Abigail Turner", "Lucas Parker", "Ella Edwards",
    "Henry Collins", "Grace Morgan", "Alexander Reed",
    "Chloe Murphy", "Raj Patel", "Ananya Sharma",
    "Omar Hassan", "Fatima Ali", "Chinedu Okeke",
    "Aisha Musa", "Kwame Mensah", "Zainab Ibrahim",
    "Pedro Silva", "Maria Gonzalez", "Jean Dupont",
    "Anna Novak"
]

# =========================
# LOCATION DATA
# =========================

locations = [

    ("New York", "USA"),
    ("Chicago", "USA"),
    ("Toronto", "Canada"),
    ("Vancouver", "Canada"),
    ("London", "United Kingdom"),
    ("Manchester", "United Kingdom"),
    ("Berlin", "Germany"),
    ("Munich", "Germany"),
    ("Paris", "France"),
    ("Lyon", "France"),
    ("Mumbai", "India"),
    ("Delhi", "India"),
    ("Sao Paulo", "Brazil"),
    ("Rio de Janeiro", "Brazil"),
    ("Johannesburg", "South Africa"),
    ("Cape Town", "South Africa"),
    ("Accra", "Ghana"),
    ("Kumasi", "Ghana"),
    ("Lagos", "Nigeria"),
    ("Abuja", "Nigeria")

]

# =========================
# ADDRESS HELPERS
# =========================

street_names = [

    "Main Street",
    "Oak Avenue",
    "Maple Drive",
    "Broadway",
    "Market Street",
    "Park Lane",
    "King Street",
    "Victoria Road",
    "High Street",
    "Sunset Boulevard"

]

# =========================
# GENERATE CUSTOMERS
# =========================

customers = []

for index, name in enumerate(
    customer_names,
    start=1
):

    customer_id = (
        f"CUST-{index:04d}"
    )

    city, country = random.choice(
        locations
    )

    address = (

        f"{random.randint(10,999)} "

        f"{random.choice(street_names)}"

    )

    email = (

        name.lower()

        .replace(" ", ".")

        + "@gmail.com"

    )

    phone = (

        f"+{random.randint(1,99)} "

        f"{random.randint(100,999)} "

        f"{random.randint(100,999)} "

        f"{random.randint(1000,9999)}"

    )

    # =========================
    # CUSTOMER STATUS
    # =========================

    status = random.choices(

        ["ACTIVE", "INACTIVE"],

        weights=[90, 10],

        k=1

    )[0]

    customers.append({

        "customer_id":
            customer_id,

        "customer_name":
            name,

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

        "status":
            status

    })

# =========================
# EXPORT
# =========================

customer_df = pd.DataFrame(
    customers
)

customer_df.to_excel(

    CUSTOMER_MASTER_FILE,

    index=False

)

# =========================
# SUMMARY
# =========================

print(
    "\n✅ Customer master data generated successfully!"
)

print(
    f"👥 Total Customers: {len(customer_df)}"
)

print(
    f"🟢 Active Customers: "
    f"{len(customer_df[customer_df['status']=='ACTIVE'])}"
)

print(
    f"🔴 Inactive Customers: "
    f"{len(customer_df[customer_df['status']=='INACTIVE'])}"
)

print(
    f"📁 Saved to: {CUSTOMER_MASTER_FILE}"
)