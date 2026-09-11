import pandas as pd
import random

# ----------------------------
# CUSTOMER LIST
# ----------------------------

customers = [
    "John Smith", "Emily Johnson", "Michael Brown", "Olivia Davis",
    "James Wilson", "Sophia Martinez", "Daniel Taylor", "Emma Anderson",
    "Liam Thomas", "Ava White", "Noah Harris", "Isabella Clark",
    "Oliver Lewis", "Mia Walker", "Elijah Hall", "Amelia Young",
    "William Scott", "Charlotte Adams", "Benjamin Carter", "Harper Mitchell",
    "Ethan Cooper", "Abigail Turner", "Lucas Parker", "Ella Edwards",
    "Henry Collins", "Grace Morgan", "Alexander Reed", "Chloe Murphy",
    "Raj Patel", "Ananya Sharma", "Omar Hassan", "Fatima Ali",
    "Chinedu Okeke", "Aisha Musa", "Kwame Mensah", "Zainab Ibrahim",
    "Pedro Silva", "Maria Gonzalez", "Jean Dupont", "Anna Novak"
]

# ----------------------------
# PRODUCTS
# ----------------------------

products = [
    "Laptop",
    "Smartphone",
    "Headphones",
    "Keyboard",
    "Mouse",
    "Monitor",
    "USB Cable",
    "External Hard Drive",
    "Webcam",
    "Office Chair",
    "Desk Lamp",
    "Tablet",
    "Router",
    "Printer",
    "Power Bank",
    "Smartwatch",
    "Speakers",
    "SSD Drive",
    "Desk",
    "Router Extender"
]

# ----------------------------
# PAYMENT STATUS
# ----------------------------

payment_status_options = [
    "Paid",
    "Unpaid",
    "Partially Paid"
]

payment_status_weights = [
    70,
    20,
    10
]


# ----------------------------
# GENERATE 300 RECORDS
# ----------------------------

data = []

for _ in range(300):

    row = {
        "customer": random.choice(customers),
        "product": random.choice(products),
        "quantity": random.randint(1, 10),

        "payment_status": random.choices(
            payment_status_options,
            weights=payment_status_weights
        )[0]
    }

    data.append(row)

# ----------------------------
# EXPORT TO EXCEL
# ----------------------------

df = pd.DataFrame(data)

df.to_excel(
    "invoice_input_data_300.xlsx",
    index=False
)

print("✅ User input file created successfully!")


#=================================================
#PRODUCT MASTER DATA
#===================================================


products = [

    {
        "product": "Laptop",
        "category": "Electronics",
        "unit_price": 750000,
        "vat_rate": 7.5
    },

    {
        "product": "Smartphone",
        "category": "Electronics",
        "unit_price": 300000,
        "vat_rate": 7.5
    },

    {
        "product": "Headphones",
        "category": "Electronics",
        "unit_price": 50000,
        "vat_rate": 7.5
    },

    {
        "product": "Keyboard",
        "category": "Office Equipment",
        "unit_price": 25000,
        "vat_rate": 7.5
    },

    {
        "product": "Mouse",
        "category": "Office Equipment",
        "unit_price": 15000,
        "vat_rate": 7.5
    },

    {
        "product": "Monitor",
        "category": "Electronics",
        "unit_price": 200000,
        "vat_rate": 7.5
    },

    {
        "product": "USB Cable",
        "category": "Accessories",
        "unit_price": 5000,
        "vat_rate": 7.5
    },

    {
        "product": "External Hard Drive",
        "category": "Storage",
        "unit_price": 120000,
        "vat_rate": 7.5
    },

    {
        "product": "Webcam",
        "category": "Electronics",
        "unit_price": 60000,
        "vat_rate": 7.5
    },

    {
        "product": "Office Chair",
        "category": "Furniture",
        "unit_price": 180000,
        "vat_rate": 7.5
    },

    {
        "product": "Desk Lamp",
        "category": "Furniture",
        "unit_price": 30000,
        "vat_rate": 7.5
    },

    {
        "product": "Tablet",
        "category": "Electronics",
        "unit_price": 250000,
        "vat_rate": 7.5
    },

    {
        "product": "Router",
        "category": "Networking",
        "unit_price": 70000,
        "vat_rate": 7.5
    },

    {
        "product": "Printer",
        "category": "Office Equipment",
        "unit_price": 150000,
        "vat_rate": 7.5
    },

    {
        "product": "Power Bank",
        "category": "Accessories",
        "unit_price": 40000,
        "vat_rate": 7.5
    },

    {
        "product": "Smartwatch",
        "category": "Electronics",
        "unit_price": 120000,
        "vat_rate": 7.5
    },

    {
        "product": "Speakers",
        "category": "Electronics",
        "unit_price": 80000,
        "vat_rate": 7.5
    },

    {
        "product": "SSD Drive",
        "category": "Storage",
        "unit_price": 100000,
        "vat_rate": 7.5
    },

    {
        "product": "Desk",
        "category": "Furniture",
        "unit_price": 220000,
        "vat_rate": 7.5
    },

    {
        "product": "Router Extender",
        "category": "Networking",
        "unit_price": 45000,
        "vat_rate": 7.5
    }
]

df = pd.DataFrame(products)

df.to_excel(
    "product_master_data.xlsx",
    index=False
)

print("✅ Product master file created successfully!")