import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==================================
# PROJECT ROOT FIX
# ==================================

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# ==================================
# IMPORTS
# ==================================

from src.paths import (
    PRODUCT_MASTER_FILE,
    PROCESSED_INVOICES_FILE,
    LOGO_PATH,
    REPORTS_DIR,
    ensure_directories
)

from src.live_invoice_engine import (
    create_live_invoice
)

from src.customer_engine import (
    load_customers,
    get_customer_names,
    get_customer_details,
    add_customer,
    customer_exists,
    update_customer,
    update_customer_status,
    get_all_customer_names
)

from src.customer_id_engine import (
    generate_customer_id
)

from src.search_engine import (
    search_by_invoice_id,
    search_by_customer,
    search_by_order_id,
    search_by_status,
    get_invoice_summary
)

from src.payment_engine import (
    record_payment,
    get_recent_payments
)

ensure_directories()
# ==================================
# LOAD DATA
# ==================================

products_df = pd.read_excel(
    PRODUCT_MASTER_FILE
)

customers_df = load_customers()

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="Smart Invoice System",
    layout="wide"
)

# Main page title removed — branding lives in the sidebar logo/markdown
# to reclaim vertical space at the top of every page.

# ==================================
# SIDEBAR
# ==================================

st.sidebar.image(
    LOGO_PATH,
    width=280
)

st.sidebar.markdown(
    """
    ### Smart Invoice System
    """
)

st.sidebar.divider()

# =============================================================
# MODULE NAVIGATION
# =============================================================

if "menu" not in st.session_state:

    st.session_state.menu = (
        "🏠 Home"
    )

# ==================================
# ACTIVE-BUTTON HIGHLIGHT STYLING
# Streamlit's "primary" button type gives the active nav item a filled
# look; this override just swaps the default red for the brand teal so
# it matches the rest of the app.
# ==================================

st.sidebar.markdown(
    """
    <style>
    section[data-testid="stSidebar"] button[kind="primary"] {
        background-color: rgba(46, 139, 139, 0.14) !important;
        border: 1px solid rgba(46, 139, 139, 0.45) !important;
        color: #1B2A4A !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: rgba(46, 139, 139, 0.20) !important;
        border-color: rgba(46, 139, 139, 0.60) !important;
        color: #1B2A4A !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid transparent;
    }
    </style>
    """,
    unsafe_allow_html=True
)

NAV_ITEMS = [
    "🏠 Home",
    "👥 Customer Management",
    "🧾 Live Invoice",
    "💳 Payments & Receivables",
    "🔍 Invoice Search",
    "📈 Dashboard Analytics",
    "📁 Data Explorer",
]

for nav_label in NAV_ITEMS:

    is_active = (st.session_state.menu == nav_label)

    if st.sidebar.button(
        nav_label,
        use_container_width=True,
        key=f"nav_{nav_label}",
        type="primary" if is_active else "secondary"
    ):
        st.session_state.menu = nav_label
        st.rerun()

menu = st.session_state.menu


# ==================================================
# HOME PAGE
# ===================================================

if menu == "🏠 Home":

    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background-color: #F8F9FB;
            border: 1px solid #E3E6EC;
            border-radius: 8px;
            padding: 10px 10px 8px 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            font-size: 0.8rem;
            color: #1B2A4A;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.3rem;
            color: #1B2A4A;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Welcome Back 👋")

    now = pd.Timestamp.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_label = now.strftime("%B %Y")

    # ==================================
    # LOAD DATA
    # ==================================

    if os.path.exists(PROCESSED_INVOICES_FILE):
        _home_df = pd.read_excel(PROCESSED_INVOICES_FILE)
    else:
        _home_df = pd.DataFrame()

    _customers_df = load_customers()

    if not _home_df.empty:
        _home_df["invoice_date"] = pd.to_datetime(_home_df["invoice_date"])

    # ==================================
    # KPI CALCULATIONS — current month scope
    # ==================================

    if not _home_df.empty:

        _month_df = _home_df[_home_df["invoice_date"] >= this_month_start]

        total_revenue_month = (
            _month_df.groupby("invoice_id")["total_amount"].first().sum()
            if "invoice_id" in _month_df.columns
            else _month_df["total_amount"].sum()
        )

        outstanding_month = (
            _month_df.groupby("invoice_id")["balance_due"].first().sum()
            if "balance_due" in _month_df.columns and "invoice_id" in _month_df.columns
            else 0
        )

    else:
        total_revenue_month = 0
        outstanding_month = 0

    def format_currency(value):
        if value >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"${value/1_000:.1f}K"
        return f"${value:,.0f}"

    # ==================================
    # KPI CARDS
    # ==================================

    with st.container(border=True):

        st.caption(f"📅 Figures below reflect **{month_label}** (current month) only.")

        hk1, hk2 = st.columns(2)

        with hk1:
            st.metric("💰 Total Revenue (This Month)", format_currency(total_revenue_month))

        with hk2:
            st.metric("⚠️ Outstanding (This Month)", format_currency(outstanding_month))

    # ==================================
    # QUICK ACTIONS
    # ==================================

    st.markdown("##### ⚡ Quick Actions")

    qa1, qa2, qa3 = st.columns(3)

    with qa1:
        if st.button("🧾 Create Invoice", use_container_width=True):
            st.session_state.menu = "🧾 Live Invoice"
            st.rerun()

    with qa2:
        if st.button("💳 Record Payment", use_container_width=True):
            st.session_state.menu = "💳 Payments & Receivables"
            st.rerun()

    with qa3:
        if st.button("👥 Add Customer", use_container_width=True):
            st.session_state.menu = "👥 Customer Management"
            st.rerun()

    # ==================================
    # RECENT INVOICES + RECENT PAYMENTS
    # ==================================

    rc1, rc2 = st.columns(2)

    with rc1:

        with st.container(border=True):

            st.markdown("##### Recent Invoices")

            if _home_df.empty:

                st.info("📄 No Invoices Yet\n\nCreate your first invoice to begin.")

            else:

                recent_invoices = (
                    _home_df[
                        [c for c in [
                            "invoice_id", "customer", "invoice_date",
                            "total_amount", "payment_status"
                        ] if c in _home_df.columns]
                    ]
                    .drop_duplicates(subset="invoice_id")
                    .sort_values("invoice_date", ascending=False)
                    .head(5)
                )

                st.dataframe(
                    recent_invoices,
                    use_container_width=True,
                    hide_index=True,
                )

    with rc2:

        with st.container(border=True):

            st.markdown("##### Recent Payments")

            recent_payments = get_recent_payments(limit=5)

            if recent_payments.empty:

                st.info("📄 No Payments Yet\n\nRecord your first payment to begin.")

            else:

                display_cols = [
                    c for c in [
                        "payment_id", "invoice_id", "customer",
                        "amount_paid", "payment_method", "payment_date"
                    ] if c in recent_payments.columns
                ]

                st.dataframe(
                    recent_payments[display_cols],
                    use_container_width=True,
                    hide_index=True,
                )


# ==================================================
# CUSTOMER MANAGEMENT
# ===================================================

elif menu == "👥 Customer Management":

    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background-color: #F8F9FB;
            border: 1px solid #E3E6EC;
            border-radius: 8px;
            padding: 10px 10px 8px 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            font-size: 0.8rem;
            color: #1B2A4A;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.3rem;
            color: #1B2A4A;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.header("Customer Management")

    # ==================================
    # KPI SUMMARY CARDS (before tabs/tables)
    # ==================================

    all_customers_df = load_customers()

    total_customers = len(all_customers_df)

    if not all_customers_df.empty and "status" in all_customers_df.columns:
        active_customers = (
            all_customers_df["status"].astype(str).str.upper() == "ACTIVE"
        ).sum()
        inactive_customers = (
            all_customers_df["status"].astype(str).str.upper() == "INACTIVE"
        ).sum()
    else:
        active_customers = 0
        inactive_customers = 0

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.metric("👥 Total Customers", total_customers)
    with kpi2:
        st.metric("🟢 Active Customers", active_customers)
    with kpi3:
        st.metric("🔴 Inactive Customers", inactive_customers)

    st.divider()

    # ==================================
    # TABS — Add | Edit | List
    # ==================================

    tab_add, tab_edit, tab_list = st.tabs(
        ["➕ Add Customer", "✏️ Edit Customer", "📋 Customer List"]
    )

    # ----------------------------------
    # TAB 1 — ADD CUSTOMER
    # ----------------------------------

    with tab_add:

        with st.container(border=True):

            st.subheader("Add Customer")

            customer_name = st.text_input("Customer Name")

            phone = st.text_input("Phone Number")

            email = st.text_input("Email Address")

            address = st.text_area("Address")

            city = st.text_input("City")

            country = st.text_input("Country")

            if st.button("Add Customer"):

                if customer_name.strip() == "":

                    st.error("Customer name is required.")

                elif customer_exists(customer_name):

                    st.warning("Customer already exists.")

                else:

                    customer_data = {

                        "customer_id": generate_customer_id(),
                        "customer_name": customer_name,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "city": city,
                        "country": country,
                        "status": "ACTIVE"

                    }

                    add_customer(customer_data)

                    st.success(f"Customer {customer_data['customer_id']} created.")

                    st.rerun()

    # ----------------------------------
    # TAB 2 — EDIT CUSTOMER
    # ----------------------------------

    with tab_edit:

        with st.container(border=True):

            st.subheader("Edit Customer")

            customers_df = load_customers()

            if not customers_df.empty:

                customer_options = (
                    ["-- Select Customer --"] + get_all_customer_names()
                )

                selected_customer = st.selectbox(
                    "Select Customer", customer_options
                )

                if selected_customer != "-- Select Customer --":

                    customer_row = customers_df[
                        customers_df["customer_name"] == selected_customer
                    ].iloc[0]

                    edit_name = st.text_input(
                        "Customer Name",
                        value=str(customer_row["customer_name"])
                    )

                    edit_phone = st.text_input(
                        "Phone",
                        value=str(customer_row["phone"])
                    )

                    edit_email = st.text_input(
                        "Email",
                        value=str(customer_row["email"])
                    )

                    edit_address = st.text_area(
                        "Address",
                        value=str(customer_row["address"])
                    )

                    edit_city = st.text_input(
                        "City",
                        value=str(customer_row["city"])
                    )

                    edit_country = st.text_input(
                        "Country",
                        value=str(customer_row["country"])
                    )

                    current_status = str(customer_row["status"]).upper()

                    status_options = ["ACTIVE", "INACTIVE"]

                    status_index = 0 if current_status == "ACTIVE" else 1

                    customer_status = st.selectbox(
                        "Customer Status",
                        status_options,
                        index=status_index
                    )

                    if st.button("Update Customer"):

                        update_customer(
                            customer_row["customer_id"],
                            {
                                "customer_name": edit_name,
                                "phone": edit_phone,
                                "email": edit_email,
                                "address": edit_address,
                                "city": edit_city,
                                "country": edit_country
                            }
                        )

                        update_customer_status(
                            customer_row["customer_id"],
                            customer_status
                        )

                        st.success("Customer Updated Successfully")

                        st.rerun()

            else:

                st.info("📄 No Customers Yet\n\nAdd your first customer to begin.")

    # ----------------------------------
    # TAB 3 — CUSTOMER LIST
    # ----------------------------------

    with tab_list:

        with st.container(border=True):

            st.subheader("Customer List")

            customers_df = load_customers()

            if customers_df.empty:

                st.info("📄 No Customers Yet\n\nAdd your first customer to begin.")

            else:

                # ==================================
                # SEARCH BAR
                # ==================================

                search_query = st.text_input(
                    "🔍 Search Customer",
                    placeholder="Search by name, phone, email, or city..."
                )

                display_df = customers_df.copy()

                if search_query.strip() != "":

                    query_lower = search_query.strip().lower()

                    search_cols = [
                        c for c in ["customer_name", "phone", "email", "city"]
                        if c in display_df.columns
                    ]

                    mask = pd.Series(False, index=display_df.index)

                    for col in search_cols:
                        mask = mask | display_df[col].astype(str).str.lower().str.contains(
                            query_lower, na=False
                        )

                    display_df = display_df[mask]

                if display_df.empty:

                    st.info("📄 No Matching Customers\n\nTry a different search term.")

                else:

                    # ==================================
                    # STATUS BADGES
                    # ==================================

                    def _status_badge(status_value):
                        status_upper = str(status_value).upper()
                        if status_upper == "ACTIVE":
                            return "🟢 ACTIVE"
                        elif status_upper == "INACTIVE":
                            return "🔴 INACTIVE"
                        return status_value

                    table_df = display_df.copy()

                    if "status" in table_df.columns:
                        table_df["status"] = table_df["status"].apply(_status_badge)

                    # ==================================
                    # BETTER TABLE — only key columns, renamed for clarity
                    # ==================================

                    column_map = {
                        "customer_id": "ID",
                        "customer_name": "Customer",
                        "phone": "Phone",
                        "city": "City",
                        "status": "Status",
                    }

                    visible_cols = [c for c in column_map.keys() if c in table_df.columns]

                    table_df = table_df[visible_cols].rename(columns=column_map)

                    st.dataframe(
                        table_df,
                        use_container_width=True,
                        hide_index=True,
                    )


# ==================================================
# LIVE INVOICE
# ==================================================

elif menu == "🧾 Live Invoice":

    st.header("Create Live Invoice")

    if "invoice_items" not in st.session_state:
        st.session_state["invoice_items"] = []

    customer_tab, items_tab, payment_tab, preview_tab = st.tabs([
        "👤 Customer",
        "🛒 Invoice Builder",
        "💳 Payment",
        "📄 Invoice Preview"
    ])

    # ==================================
    # TAB 1 — CUSTOMER
    # ==================================

    with customer_tab:

        with st.container(border=True):

            st.subheader("👤 Customer")

            customer_options = (
                ["-- Select Customer --"] + get_customer_names()
            )

            customer_name = st.selectbox(
                "Select Customer",
                customer_options,
                key="live_invoice_customer"
            )

            customer_details = None

            if customer_name != "-- Select Customer --":

                customer_details = get_customer_details(customer_name)

                if customer_details is not None:

                    col1, col2 = st.columns(2)

                    with col1:

                        st.info(f"Customer ID: {customer_details['customer_id']}")

                        st.write(f"📞 {customer_details['phone']}")

                        st.write(f"📧 {customer_details['email']}")

                    with col2:

                        st.write(f"🏠 {customer_details['address']}")

                        st.write(
                            f"🌍 {customer_details['city']}, "
                            f"{customer_details['country']}"
                        )

            else:

                st.info("Select a customer to continue.")

    # ==================================
    # TAB 2 — INVOICE BUILDER
    # ==================================

    with items_tab:

        with st.container(border=True):

            st.subheader("🛒 Invoice Builder")

            # =========================
            # ADD ITEM SECTION
            # =========================

            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:

                product = st.selectbox(
                    "Product",
                    products_df["product"].tolist(),
                    key="live_invoice_product"
                )

            with col2:

                quantity = st.number_input(
                    "Qty",
                    min_value=1,
                    value=1,
                    key="live_invoice_quantity"
                )

            with col3:

                st.write("")
                st.write("")

                add_item = st.button(
                    "➕ Add",
                    use_container_width=True,
                    key="live_invoice_add"
                )

            if add_item:

                product_row = products_df[
                    products_df["product"] == product
                ]

                unit_price = float(product_row["unit_price"].iloc[0])

                row_total = quantity * unit_price

                st.session_state["invoice_items"].append({
                    "product": product,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "row_total": row_total
                })

                st.success("Item Added")

            # =========================
            # CURRENT INVOICE
            # =========================

            if st.session_state["invoice_items"]:

                st.subheader("📄 Current Invoice")

                invoice_df = pd.DataFrame(st.session_state["invoice_items"])

                invoice_df_display = invoice_df.rename(columns={
                    "product": "Product",
                    "quantity": "Quantity",
                    "unit_price": "Unit Price",
                    "row_total": "Row Total"
                })

                st.dataframe(
                    invoice_df_display,
                    hide_index=True,
                    use_container_width=True
                )

                # =========================
                # REMOVE ITEM
                # =========================

                st.caption("Manage Items")

                col1, col2 = st.columns([5, 1])

                with col1:

                    remove_product = st.selectbox(
                        "Select Item",
                        invoice_df["product"].tolist(),
                        label_visibility="collapsed",
                        key="remove_invoice_item"
                    )

                with col2:

                    remove_clicked = st.button(
                        "❌",
                        use_container_width=True,
                        help="Remove Item",
                        key="remove_invoice_button"
                    )

                if remove_clicked:

                    st.session_state["invoice_items"] = [
                        item for item in st.session_state["invoice_items"]
                        if item["product"] != remove_product
                    ]

                    st.rerun()

                # =========================
                # CALCULATIONS
                # =========================

                subtotal = float(invoice_df["row_total"].sum())

                vat_amount = round(subtotal * 0.075, 2)

                grand_total = round(subtotal + vat_amount, 2)

            else:

                subtotal = 0
                vat_amount = 0
                grand_total = 0

                st.info("No items have been added yet.")

    # ==================================
    # TAB 3 — PAYMENT
    # ==================================

    with payment_tab:

        with st.container(border=True):

            st.subheader("💳 Payment & Summary")

            col1, col2 = st.columns(2)

            with col1:

                payment_amount = st.number_input(
                    "Amount Received",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    key="live_invoice_payment_amount"
                )

                st.caption(f"Entered Amount: ${payment_amount:,.2f}")

            with col2:

                payment_method = st.selectbox(
                    "Payment Method",
                    ["Cash", "Bank Transfer", "Card", "Mobile Money", "Other"],
                    key="live_invoice_payment_method"
                )

            # =========================
            # PAYMENT SUMMARY
            # =========================

            if st.session_state["invoice_items"]:

                balance_due = max(grand_total - payment_amount, 0)

                st.divider()

                summary_df = pd.DataFrame({
                    "Description": [
                        "Subtotal", "VAT (7.5%)", "Grand Total",
                        "Amount Received", "Balance Due"
                    ],
                    "Amount": [
                        f"${subtotal:,.2f}",
                        f"${vat_amount:,.2f}",
                        f"${grand_total:,.2f}",
                        f"${payment_amount:,.2f}",
                        f"${balance_due:,.2f}"
                    ]
                })

                st.dataframe(
                    summary_df,
                    hide_index=True,
                    use_container_width=True
                )

                # =========================
                # OVERPAYMENT VALIDATION
                # =========================

                if payment_amount > grand_total:
                    st.error("Amount Received cannot exceed Grand Total.")

            else:

                balance_due = 0

                st.info("Add invoice items to see payment summary.")

        # ==================================
        # GENERATE INVOICE
        # ==================================

        with st.container(border=True):

            st.subheader("Generate Invoice")

            generate_invoice = st.button(
                "🧾 Generate Invoice",
                use_container_width=True,
                key="generate_live_invoice"
            )

            if generate_invoice:

                if customer_name == "-- Select Customer --":

                    st.error("Please select a customer.")

                elif len(st.session_state["invoice_items"]) == 0:

                    st.error("Add at least one item.")

                elif payment_amount > grand_total:

                    st.error("Amount Received cannot exceed Grand Total.")

                else:

                    file_path, invoice_id = create_live_invoice(
                        customer_details,
                        st.session_state["invoice_items"]
                    )

                    # =========================
                    # RECORD INITIAL PAYMENT
                    # =========================

                    if payment_amount > 0:

                        try:

                            record_payment(invoice_id, payment_amount, payment_method)

                        except Exception as e:

                            st.error(f"Payment Error: {str(e)}")

                    st.success(f"Invoice {invoice_id} generated successfully!")

                    with open(file_path, "rb") as f:

                        st.download_button(
                            label="⬇ Download Invoice PDF",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="application/pdf"
                        )

                    st.session_state["invoice_items"] = []

    # ==================================
    # TAB 4 — INVOICE PREVIEW
    # (always reflects current session state, not just after generation)
    # ==================================

    with preview_tab:

        with st.container(border=True):

            st.subheader("📄 Invoice Preview")

            # =========================
            # COMPANY HEADER
            # =========================

            st.markdown(
                """
                <div style="
                    text-align:center;
                    padding:15px;
                    border-bottom:2px solid #D9D9D9;
                    margin-bottom:20px;
                ">
                <h2 style="margin-bottom:0;">Miracle Analytics</h2>
                <p style="color:gray;">Smart Invoice System</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # =========================
            # CUSTOMER DETAILS
            # =========================

            if customer_details is not None:

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown("### Invoice To")

                    st.write(customer_name)

                    st.write(customer_details["phone"])

                    st.write(customer_details["email"])

                with col2:

                    st.markdown("### Address")

                    st.write(customer_details["address"])

                    st.write(
                        f"{customer_details['city']}, "
                        f"{customer_details['country']}"
                    )

            else:

                st.info("Select a customer first.")

            st.divider()

            # =========================
            # INVOICE ITEMS
            # =========================

            if st.session_state["invoice_items"]:

                preview_df = pd.DataFrame(st.session_state["invoice_items"])

                preview_df_display = preview_df.rename(columns={
                    "product": "Product",
                    "quantity": "Qty",
                    "unit_price": "Unit Price",
                    "row_total": "Total"
                })

                preview_df_display["Unit Price"] = (
                    preview_df_display["Unit Price"].apply(lambda x: f"${x:,.2f}")
                )

                preview_df_display["Total"] = (
                    preview_df_display["Total"].apply(lambda x: f"${x:,.2f}")
                )

                st.table(preview_df_display)

            else:

                st.info("No items added yet.")

            st.divider()

            # =========================
            # PAYMENT STATUS
            # =========================

            if grand_total == 0:

                payment_status = "N/A"
                status_color = "#6B7280"

            elif payment_amount == 0:

                payment_status = "UNPAID"
                status_color = "#DC2626"

            elif payment_amount < grand_total:

                payment_status = "PARTIALLY PAID"
                status_color = "#F59E0B"

            else:

                payment_status = "PAID"
                status_color = "#16A34A"

            # =========================
            # INVOICE SUMMARY
            # =========================

            st.markdown(
                f"""
                <div style="
                    border-top:1px solid #D9D9D9;
                    padding-top:20px;
                    margin-top:20px;
                ">
                    <div style="display:flex; justify-content:space-between; padding:8px 0;">
                        <span>Subtotal</span>
                        <span>${subtotal:,.2f}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:8px 0;">
                        <span>VAT (7.5%)</span>
                        <span>${vat_amount:,.2f}</span>
                    </div>
                    <div style="
                        display:flex; justify-content:space-between;
                        padding:12px 0; margin-top:10px;
                        border-top:2px solid #D9D9D9;
                        font-size:20px; font-weight:bold;
                    ">
                        <span>GRAND TOTAL</span>
                        <span>${grand_total:,.2f}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:8px 0;">
                        <span>Amount Received</span>
                        <span>${payment_amount:,.2f}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:8px 0;">
                        <span>Balance Due</span>
                        <span>${balance_due:,.2f}</span>
                    </div>
                    <div style="
                        display:flex; justify-content:space-between;
                        padding:12px 0; margin-top:10px;
                        border-top:1px solid #D9D9D9;
                    ">
                        <span><b>Status</b></span>
                        <span style="color:{status_color}; font-weight:bold;">
                            {payment_status}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ==================================================
# PAYMENT TRACKING
# ==================================================

elif menu == "💳 Payments & Receivables":

    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background-color: #F8F9FB;
            border: 1px solid #E3E6EC;
            border-radius: 8px;
            padding: 10px 10px 8px 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            font-size: 0.8rem;
            color: #1B2A4A;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.3rem;
            color: #1B2A4A;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.header("Payments & Receivables")

    # ==================================
    # MODULE KPI CARDS — Paid | Partial | Unpaid (before the lookup form)
    # ==================================

    if os.path.exists(PROCESSED_INVOICES_FILE):

        _payments_df = pd.read_excel(PROCESSED_INVOICES_FILE)

        if not _payments_df.empty and "payment_status" in _payments_df.columns:

            _status_upper = _payments_df["payment_status"].astype(str).str.upper()

            paid_count = (
                _payments_df[_status_upper == "PAID"]["invoice_id"].nunique()
                if "invoice_id" in _payments_df.columns
                else (_status_upper == "PAID").sum()
            )

            partial_count = (
                _payments_df[_status_upper == "PARTIALLY PAID"]["invoice_id"].nunique()
                if "invoice_id" in _payments_df.columns
                else (_status_upper == "PARTIALLY PAID").sum()
            )

            unpaid_count = (
                _payments_df[_status_upper == "UNPAID"]["invoice_id"].nunique()
                if "invoice_id" in _payments_df.columns
                else (_status_upper == "UNPAID").sum()
            )

        else:
            paid_count = partial_count = unpaid_count = 0

    else:
        paid_count = partial_count = unpaid_count = 0

    pk1, pk2, pk3 = st.columns(3)

    with pk1:
        st.metric("🟢 Paid", paid_count)
    with pk2:
        st.metric("🟡 Partial", partial_count)
    with pk3:
        st.metric("🔴 Unpaid", unpaid_count)

    st.divider()

    # ==================================
    # INVOICE LOOKUP + RECORD PAYMENT
    # ==================================

    with st.container(border=True):

        st.subheader("Invoice Lookup")

        invoice_id = st.text_input("Invoice ID")

        if invoice_id:

            summary = get_invoice_summary(invoice_id)

            if summary is None:

                st.error("Invoice not found.")

            else:

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Invoice Total", f"${summary['invoice_total']:,.2f}")

                with col2:
                    st.metric("Amount Paid", f"${summary['amount_paid']:,.2f}")

                with col3:
                    st.metric("Balance Due", f"${summary['balance_due']:,.2f}")

                st.write(f"Customer: {summary['customer']}")

                # ==================================
                # STATUS BADGE
                # ==================================

                _status_value = str(summary["payment_status"]).upper()

                if _status_value == "PAID":
                    _badge = "🟢 PAID"
                elif _status_value == "PARTIALLY PAID":
                    _badge = "🟡 PARTIALLY PAID"
                elif _status_value == "UNPAID":
                    _badge = "🔴 UNPAID"
                else:
                    _badge = summary["payment_status"]

                st.write(f"Status: {_badge}")

                st.divider()

                payment_amount = st.number_input(
                    "Payment Amount",
                    min_value=0.0,
                    step=1.0
                )

                payment_method = st.selectbox(
                    "Payment Method",
                    ["Bank Transfer", "Cash", "Card", "Mobile Money", "Other"]
                )

                if st.button("Record Payment"):

                    try:

                        result = record_payment(
                            invoice_id,
                            payment_amount,
                            payment_method
                        )

                        st.success(
                            f"✅ Payment Recorded: {result['payment_id']}"
                        )

                        st.write(
                            f"Updated Status: {result['payment_status']}"
                        )

                        st.write(
                            f"Remaining Balance: ${result['balance_due']:,.2f}"
                        )

                        # ==================================
                        # UPDATED PDF
                        # ==================================

                        customer_name = str(result["customer"]).replace(" ", "_")

                        updated_pdf_path = os.path.join(
                            REPORTS_DIR,
                            f"{invoice_id}_{customer_name}.pdf"
                        )

                        if os.path.exists(updated_pdf_path):

                            st.success(
                                "📄 Invoice PDF updated successfully."
                            )

                            with open(updated_pdf_path, "rb") as pdf_file:

                                st.download_button(
                                    label="📄 Download Updated Invoice",
                                    data=pdf_file,
                                    file_name=os.path.basename(updated_pdf_path),
                                    mime="application/pdf"
                                )

                        else:

                            st.warning(
                                "Payment was recorded, but the updated invoice PDF could not be found."
                            )

                    except Exception as e:

                        st.error(str(e))
        else:

            st.info("📄 No Invoice Selected\n\nEnter an Invoice ID above to view payment details.")


# ==================================================
# INVOICE SEARCH
# ==================================================

elif menu == "🔍 Invoice Search":

    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background-color: #F8F9FB;
            border: 1px solid #E3E6EC;
            border-radius: 8px;
            padding: 10px 10px 8px 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            font-size: 0.8rem;
            color: #1B2A4A;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.3rem;
            color: #1B2A4A;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.header("Invoice Search")

    # ==================================
    # SEARCH
    # ==================================

    with st.container(border=True):

        st.subheader("Search")

        search_type = st.selectbox(
            "Search By",
            [
                "Invoice ID",
                "Order ID",
                "Customer",
                "Payment Status"
            ]
        )

        query = st.text_input(
            "Search Value"
        )

        if st.button(
            "🔎 Search",
            use_container_width=False
        ):

            result = pd.DataFrame()

            if search_type == "Invoice ID":

                result = search_by_invoice_id(
                    query
                )

            elif search_type == "Order ID":

                result = search_by_order_id(
                    query
                )

            elif search_type == "Customer":

                result = search_by_customer(
                    query
                )

            elif search_type == "Payment Status":

                result = search_by_status(
                    query
                )

            st.session_state[
                "_invoice_search_result"
            ] = result

            # A fresh search invalidates any previously open PDF preview
            # and re-hides the generated-invoices panel until requested again.
            st.session_state["show_generated_invoices"] = False
            st.session_state["preview_invoice_id"] = None
            st.session_state["preview_history_path"] = None

    result = st.session_state.get(
        "_invoice_search_result",
        pd.DataFrame()
    )

    # ==================================
    # SEARCH RESULTS
    # ==================================

    with st.container(border=True):

        st.subheader("Results")

        if result.empty:

            st.info(
                "📄 No Invoices Found\n\n"
                "Try a different search term or search type."
            )

        else:

            # ==================================
            # KPI CARDS
            # ==================================

            invoices_found = (
                result["invoice_id"].nunique()
                if "invoice_id" in result.columns
                else len(result)
            )

            if "payment_status" in result.columns:

                _status_upper = (
                    result["payment_status"]
                    .astype(str)
                    .str.upper()
                )

                paid_found = (
                    result[
                        _status_upper == "PAID"
                        ]["invoice_id"].nunique()
                    if "invoice_id" in result.columns
                    else (
                            _status_upper == "PAID"
                    ).sum()
                )

            else:

                paid_found = 0

            # ==================================
            # PAID AMOUNT
            # ==================================

            if (
                    "amount_paid" in result.columns
                    and "invoice_id" in result.columns
            ):

                paid_amount = (
                    result
                    .groupby("invoice_id")["amount_paid"]
                    .first()
                    .sum()
                )

            elif "amount_paid" in result.columns:

                paid_amount = result["amount_paid"].sum()

            else:

                paid_amount = 0

            if "balance_due" in result.columns:

                outstanding_found = (
                    result
                    .groupby("invoice_id")[
                        "balance_due"
                    ]
                    .first()
                    .sum()
                    if "invoice_id" in result.columns
                    else result["balance_due"].sum()
                )

            elif (
                "total_amount" in result.columns
                and "payment_status" in result.columns
            ):

                outstanding_found = (
                    result[
                        result["payment_status"]
                        .astype(str)
                        .str.upper()
                        != "PAID"
                    ]["total_amount"]
                    .sum()
                )

            else:

                outstanding_found = 0

            sk1, sk2, sk3, sk4 = st.columns(4)

            with sk1:
                st.metric(
                    "🧾 Invoices Found",
                    invoices_found
                )

            with sk2:
                st.metric(
                    "✅ Paid Invoices",
                    paid_found
                )

            with sk3:
                st.metric(
                    "💰 Paid Amount",
                    f"${paid_amount:,.2f}"
                )

            with sk4:
                st.metric(
                    "⚠️ Outstanding Balance",
                    f"${outstanding_found:,.2f}"
                )

            st.divider()

            # ==================================
            # STATUS BADGES
            # ==================================

            display_result = result.copy()

            if "payment_status" in display_result.columns:

                def _status_badge(
                    status_value
                ):

                    status_upper = (
                        str(status_value)
                        .upper()
                    )

                    if status_upper == "PAID":

                        return "🟢 PAID"

                    elif status_upper == "PARTIALLY PAID":

                        return "🟡 PARTIALLY PAID"

                    elif status_upper == "UNPAID":

                        return "🔴 UNPAID"

                    return status_value

                display_result[
                    "payment_status"
                ] = (
                    display_result[
                        "payment_status"
                    ]
                    .apply(_status_badge)
                )

            st.success(
                f"{invoices_found} invoice(s) found."
            )

            st.dataframe(
                display_result,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # ==================================
            # GENERATED INVOICE DOCUMENTS
            # ==================================

            if "show_generated_invoices" not in st.session_state:
                st.session_state["show_generated_invoices"] = False

            if "preview_invoice_id" not in st.session_state:
                st.session_state["preview_invoice_id"] = None

            if "preview_history_path" not in st.session_state:
                st.session_state["preview_history_path"] = None

            view_generated_clicked = st.button(
                "📄 View Generated Invoices",
                use_container_width=False
            )

            if view_generated_clicked:
                st.session_state["show_generated_invoices"] = True

            # Gate on the persisted flag (not the transient button click) so
            # the panel stays open across reruns triggered by the preview /
            # download buttons inside it.
            if st.session_state["show_generated_invoices"]:

                if "invoice_id" in result.columns:
                    invoice_ids = (
                        result["invoice_id"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )
                else:
                    invoice_ids = []

                if not invoice_ids:

                    st.warning(
                        "No invoice documents are available for this search."
                    )

                else:

                    header_col1, header_col2 = st.columns([6, 1])

                    with header_col1:
                        st.subheader(
                            "Generated Invoice Documents"
                        )

                    with header_col2:
                        st.markdown(
                            "<div style='height: 0.6rem;'></div>",
                            unsafe_allow_html=True
                        )
                        close_clicked = st.button(
                            "✕ Close",
                            key="close_generated_invoices",
                            use_container_width=True
                        )

                        if close_clicked:
                            st.session_state["show_generated_invoices"] = False
                            st.session_state["preview_invoice_id"] = None
                            st.session_state["preview_history_path"] = None
                            st.rerun()

                    for current_invoice_id in invoice_ids:

                        invoice_rows = result[
                            result["invoice_id"].astype(str)
                            == current_invoice_id
                            ]

                        if invoice_rows.empty:
                            continue

                        # ==================================
                        # FIND ALL PDFs FOR THIS INVOICE
                        # The most recently written file is treated as the
                        # "current" version; any earlier ones (e.g. before a
                        # payment update regenerated the PDF) are shown below
                        # as previous versions.
                        # ==================================

                        current_pdf_matches = sorted(
                            [
                                filename
                                for filename in os.listdir(REPORTS_DIR)
                                if filename.startswith(
                                f"{current_invoice_id}_"
                            )
                                   and filename.lower().endswith(".pdf")
                            ],
                            key=lambda fn: os.path.getmtime(
                                os.path.join(REPORTS_DIR, fn)
                            ),
                            reverse=True,
                        )

                        current_pdf_path = (
                            os.path.join(
                                REPORTS_DIR,
                                current_pdf_matches[0]
                            )
                            if current_pdf_matches
                            else None
                        )

                        historical_matches = current_pdf_matches[1:]

                        # ==================================
                        # CURRENT INVOICE
                        # ==================================

                        st.markdown(
                            f"### 🧾 {current_invoice_id}"
                        )

                        if current_pdf_path and os.path.exists(
                                current_pdf_path
                        ):

                            current_col1, current_col2 = st.columns(2)

                            # ----------------------------------
                            # PREVIEW BUTTON
                            # ----------------------------------

                            with current_col1:

                                preview_clicked = st.button(
                                    "👁️ Preview Current Invoice",
                                    key=f"preview_current_{current_invoice_id}"
                                )

                                if preview_clicked:
                                    st.session_state["preview_invoice_id"] = current_invoice_id
                                    st.session_state["preview_history_path"] = None

                            # ----------------------------------
                            # DOWNLOAD BUTTON
                            # ----------------------------------

                            with current_col2:

                                with open(
                                        current_pdf_path,
                                        "rb"
                                ) as pdf_file:
                                    current_pdf_bytes = (
                                        pdf_file.read()
                                    )

                                st.download_button(
                                    label="📄 Download Current Invoice",
                                    data=current_pdf_bytes,
                                    file_name=os.path.basename(
                                        current_pdf_path
                                    ),
                                    mime="application/pdf",
                                    key=(
                                        f"download_current_"
                                        f"{current_invoice_id}"
                                    )
                                )

                            # ==================================
                            # SHOW CURRENT PDF PREVIEW
                            # ==================================

                            if st.session_state.get(
                                    "preview_invoice_id"
                            ) == current_invoice_id:

                                st.markdown(
                                    "#### 👁️ Invoice Preview"
                                )

                                with open(
                                        current_pdf_path,
                                        "rb"
                                ) as pdf_file:
                                    pdf_bytes = pdf_file.read()

                                st.pdf(
                                    pdf_bytes,
                                    height=700
                                )

                            # ==================================
                            # HISTORICAL VERSIONS
                            # ==================================

                            if historical_matches:

                                st.markdown("#### 🕓 Previous Versions")

                                for version_index, filename in enumerate(
                                        historical_matches, start=1
                                ):

                                    history_path = os.path.join(
                                        REPORTS_DIR, filename
                                    )

                                    version_col1, version_col2 = st.columns(2)

                                    # ----------------------------------
                                    # HISTORICAL PREVIEW
                                    # ----------------------------------

                                    with version_col1:

                                        preview_version_clicked = st.button(
                                            f"👁️ Preview Version {version_index}",
                                            key=(
                                                f"preview_history_"
                                                f"{current_invoice_id}_"
                                                f"{version_index}"
                                            )
                                        )

                                        if preview_version_clicked:
                                            st.session_state[
                                                "preview_history_path"
                                            ] = history_path
                                            st.session_state[
                                                "preview_invoice_id"
                                            ] = None

                                    # ----------------------------------
                                    # HISTORICAL DOWNLOAD
                                    # ----------------------------------

                                    with version_col2:

                                        with open(
                                                history_path,
                                                "rb"
                                        ) as pdf_file:
                                            history_pdf_bytes = (
                                                pdf_file.read()
                                            )

                                        st.download_button(
                                            label=(
                                                f"📄 Download Version "
                                                f"{version_index}"
                                            ),
                                            data=history_pdf_bytes,
                                            file_name=filename,
                                            mime="application/pdf",
                                            key=(
                                                f"download_history_"
                                                f"{current_invoice_id}_"
                                                f"{version_index}"
                                            )
                                        )

                                    # ----------------------------------
                                    # SHOW HISTORICAL PDF PREVIEW
                                    # ----------------------------------

                                    if st.session_state.get(
                                            "preview_history_path"
                                    ) == history_path:

                                        st.markdown(
                                            f"#### 👁️ Version "
                                            f"{version_index} Preview"
                                        )

                                        with open(
                                                history_path,
                                                "rb"
                                        ) as pdf_file:

                                            history_pdf_bytes = (
                                                pdf_file.read()
                                            )

                                        st.pdf(
                                            history_pdf_bytes,
                                            height=700
                                        )

                            else:

                                st.caption(
                                    "No previous PDF versions archived yet."
                                )

                        else:

                            st.info(
                                "Current invoice PDF not found."
                            )

                        st.divider()

# ==================================================
# DASHBOARD ANALYTICS
# ==================================================

elif menu == "📈 Dashboard Analytics":

    def format_currency(value):

        if value >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"${value/1_000:.1f}K"
        return f"${value:,.0f}"

    # ==================================
    # LIGHT / MODERN CARD STYLING
    # All charts now sit inside bordered "panel" cards (see CARD_BG below)
    # to match the reference dashboard look. Colors are tuned for the
    # light theme set in .streamlit/config.toml.
    # ==================================

    CARD_BG = "#F4F6F9"
    CARD_BORDER = "transparent"
    AXIS_TEXT = "#000000"
    GRID_COLOR = "#E3E6EC"
    LABEL_COLOR = "#000000"

    st.markdown(
        """
        <style>
        div.block-container {
            padding-top: 2.5rem;
            padding-bottom: 1rem;
        }

        h5, h6 {
            margin-top: 0.2rem !important;
            margin-bottom: 0.4rem !important;
        }

        .chart-card {
            background-color: #F4F6F9;
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        }

        /* Dashboard Chart Cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #F4F6F9;
            border: none !important;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow:
                0 3px 6px rgba(0,0,0,0.04),
                0 10px 25px rgba(0,0,0,0.08);
        }

        /* Individual KPI metric — grey card with shadow */
        div[data-testid="stMetric"] {
            background-color: #F4F6F9;
            border: none !important;
            border-radius: 8px;
            padding: 16px 16px 12px 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        }

        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            font-size: 0.85rem;
            color: #000000;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
            color: #000000;
        }

        /* Export buttons — borderless, shadow-only, modern pill style */
        div[data-testid="column"] button {
            min-height: 42px;
            font-size: 0.9rem;
            padding: 0.6rem 1.2rem;
            white-space: nowrap;
            border: none !important;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.10);
            background-color: #FFFFFF;
            color: #1B2A4A;
            font-weight: 500;
        }
        div[data-testid="column"] button:hover {
            border: none !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.14);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    COLOR_SEQUENCE = [
        "#1B2A4A", "#2E8B8B", "#5B7FBE",
        "#B7950B", "#1E8449", "#B03A2E"
    ]
    STATUS_COLOR_MAP = {
        "PAID": "#1E8449",
        "PARTIALLY PAID": "#B7950B",
        "UNPAID": "#B03A2E",
    }


    def _dark_chart_layout(fig, height):

        fig.update_layout(

            plot_bgcolor=CARD_BG,

            paper_bgcolor=CARD_BG,

            font=dict(
                color=AXIS_TEXT,
                size=13
            ),

            height=height

        )

        fig.update_xaxes(

            showgrid=False,

            showline=False,

            zeroline=False,

            color=AXIS_TEXT,

            tickfont=dict(
                size=12,
                color="#000000"
            )

        )

        fig.update_yaxes(

            showgrid=False,

            showline=False,

            zeroline=False,

            color=AXIS_TEXT,

            tickfont=dict(
                size=12,
                color="#000000"
            )

        )

        return fig
    # ==================================
    # HEADER ROW — Title (left) + Export buttons (top-right)
    # ==================================

    header_left, header_right = st.columns([2.2, 3.2])

    with header_left:
        st.markdown("### 📈 Dashboard Analytics")

    with header_right:
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            export_csv_clicked = st.button(
                "⬇ Export CSV", use_container_width=True
            )
        with exp_col2:
            export_pdf_clicked = st.button(
                "⬇ Export PDF", use_container_width=True
            )

    if os.path.exists(PROCESSED_INVOICES_FILE):

        df = pd.read_excel(PROCESSED_INVOICES_FILE)

        if not df.empty:

            df["invoice_date"] = pd.to_datetime(df["invoice_date"])

            if "due_date" in df.columns:
                df["due_date"] = pd.to_datetime(df["due_date"])

            # ==================================
            # FILTERS — full-width row, just under the header
            # ==================================

            with st.container(border=True):

                f1, f2, f3, f4 = st.columns(4)

                years = sorted(df["invoice_date"].dt.year.unique().tolist())

                months = [
                    "January", "February", "March", "April",
                    "May", "June", "July", "August",
                    "September", "October", "November", "December"
                ]

                categories = sorted(df["category"].dropna().unique().tolist())
                statuses = sorted(df["payment_status"].dropna().unique().tolist())

                with f1:
                    selected_year = st.selectbox("Year", ["All"] + years)

                with f2:
                    selected_month = st.selectbox("Month", ["All"] + months)

                with f3:
                    selected_category = st.selectbox("Category", ["All"] + categories)

                with f4:
                    selected_status = st.selectbox("Payment Status", ["All"] + statuses)

            filtered_df = df.copy()

            # NOTE: Year and Month are applied as INDEPENDENT filters.
            # Selecting "January" with Year="All" shows every January across
            # all years combined, rather than requiring an exact Year+Month
            # combination to exist (which previously produced empty/zero
            # results whenever that specific pair had no data).
            if selected_year != "All":
                filtered_df = filtered_df[
                    filtered_df["invoice_date"].dt.year == selected_year
                ]

            if selected_month != "All":
                month_num = months.index(selected_month) + 1
                filtered_df = filtered_df[
                    filtered_df["invoice_date"].dt.month == month_num
                ]

            if selected_category != "All":
                filtered_df = filtered_df[
                    filtered_df["category"] == selected_category
                ]

            if selected_status != "All":
                filtered_df = filtered_df[
                    filtered_df["payment_status"] == selected_status
                ]

            # ==================================
            # KPI CALCULATIONS
            # ==================================

            registered_customers = len(load_customers())

            purchasing_customers = (
                filtered_df["customer_id"].nunique()
                if "customer_id" in filtered_df.columns
                else filtered_df["customer"].nunique()
            )

            total_invoices = filtered_df["invoice_id"].nunique()

            paid_invoices = (
                filtered_df[filtered_df["payment_status"] == "PAID"]
                ["invoice_id"]
                .nunique()
            )

            total_revenue = (
                filtered_df.groupby("invoice_id")["total_amount"].first().sum()
            )

            outstanding_balance = (
                filtered_df.groupby("invoice_id")["balance_due"].first().sum()
                if "balance_due" in filtered_df.columns
                else 0
            )

            amount_collected = total_revenue - outstanding_balance

            collection_rate = (
                (amount_collected / total_revenue) * 100
                if total_revenue > 0 else 0
            )

            # ==================================
            # KPI STRIP — 4 per row (8 KPIs total), each in its own card
            # ==================================

            kpi_row1 = st.columns(4)

            with kpi_row1[0]:
                st.metric("👥 Registered Customers", registered_customers)
            with kpi_row1[1]:
                st.metric("🛒 Purchasing Customers", purchasing_customers)
            with kpi_row1[2]:
                st.metric("🧾 Total Invoices", total_invoices)
            with kpi_row1[3]:
                st.metric("✅ Paid Invoices", paid_invoices)

            kpi_row2 = st.columns(4)

            with kpi_row2[0]:
                st.metric("💰 Total Revenue", format_currency(total_revenue))
            with kpi_row2[1]:
                st.metric("🏦 Amount Collected", format_currency(amount_collected))
            with kpi_row2[2]:
                st.metric("📈 Collection Rate", f"{collection_rate:.0f}%")
            with kpi_row2[3]:
                st.metric("⚠️ Outstanding Balance", format_currency(outstanding_balance))

            # ==================================
            # MONTHLY REVENUE TREND
            # X-axis is always exactly 12 slots: January through December.
            # - If a specific Year is selected, filtered_df already only
            #   contains that year's rows, so each month shows that year's
            #   total only.
            # - If Year = "All", filtered_df spans every year, so each
            #   calendar month here is the SUM across all years combined
            #   (e.g. January = Jan 2024 + Jan 2025 + Jan 2026 totals).
            # Either way the chart never spans multiple years left-to-right.
            # ==================================

            month_order = [
                "January", "February", "March", "April",
                "May", "June", "July", "August",
                "September", "October", "November", "December"
            ]

            monthly_revenue = (
                filtered_df
                .assign(month_name=filtered_df["invoice_date"].dt.month_name())
                .groupby("month_name")["total_amount"]
                .sum()
                .reindex(month_order, fill_value=0)
                .reset_index()
            )

            monthly_revenue.columns = ["month_name", "total_amount"]

            max_revenue = monthly_revenue[
                "total_amount"
            ].max()

            fig_trend = px.line(
                monthly_revenue,
                x="month_name",
                y="total_amount",
                markers=True,
                text="total_amount",
                color_discrete_sequence=[COLOR_SEQUENCE[0]],
                category_orders={"month_name": month_order},
            )

            fig_trend.update_traces(
                line=dict(width=2.5),
                marker=dict(size=7, color=COLOR_SEQUENCE[0]),
                texttemplate="%{text:,.0f}",
                textposition="top center",
                textfont=dict(size=12, color="#000000"),
                hovertemplate="%{x}: %{y:,.0f}<extra></extra>",
            )

            fig_trend.update_layout(
                margin=dict(
                    t=90,
                    b=10,
                    l=10,
                    r=10
                ),
                yaxis=dict(
                    range=[
                        0,
                        max_revenue * 1.25
                    ]
                ),
                yaxis_title=None,
                xaxis_title=None,
            )

            _dark_chart_layout(fig_trend, height=280)

            with st.container():
                st.markdown("##### Monthly Revenue Trend")

                st.plotly_chart(
                    fig_trend,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

            # ==================================
            # ROW — Yearly Revenue | Revenue By Category
            # ==================================

            col1, col2 = st.columns(2)

            with col1:

                with st.container():
                    st.markdown("##### Yearly Revenue")

                    yearly_revenue = (
                        filtered_df
                        .groupby(filtered_df["invoice_date"].dt.year)["total_amount"]
                        .sum()
                        .reset_index()
                        .sort_values("invoice_date")
                    )

                    fig_yearly = px.bar(
                        yearly_revenue,
                        x="invoice_date",
                        y="total_amount",
                        text="total_amount",
                        color_discrete_sequence=[COLOR_SEQUENCE[1]],
                    )

                    fig_yearly.update_traces(
                        texttemplate="%{text:,.0f}",
                        textposition="outside",
                        textfont=dict(size=12, color="#000000"),
                    )

                    fig_yearly.update_layout(
                        margin=dict(t=30, b=10, l=10, r=10),
                        xaxis_title=None,
                        yaxis_title=None,
                        xaxis=dict(type="category"),
                    )

                    _dark_chart_layout(
                        fig_yearly,
                        height=200
                    )

                    st.plotly_chart(
                        fig_yearly,
                        use_container_width=True,
                        config={"displayModeBar": False}
                    )

            with col2:

                with st.container():
                    st.markdown("##### Revenue By Category")

                    category_revenue = (
                        filtered_df
                        .groupby("category")["total_amount"]
                        .sum()
                        .reset_index()
                        .sort_values(
                            "total_amount",
                            ascending=False
                        )
                    )

                    fig_category = px.bar(
                        category_revenue,
                        x="category",
                        y="total_amount",
                        text="total_amount",
                        color="category",
                        color_discrete_sequence=COLOR_SEQUENCE,
                    )

                    fig_category.update_traces(
                        texttemplate="%{text:,.0f}",
                        textposition="outside",
                        textfont=dict(
                            size=12,
                            color="#000000"
                        ),
                    )

                    fig_category.update_layout(
                        margin=dict(
                            t=10,
                            b=10,
                            l=10,
                            r=10
                        ),
                        showlegend=False,
                        xaxis_title=None,
                        yaxis_title=None,
                    )

                    _dark_chart_layout(
                        fig_category,
                        height=200
                    )

                    st.plotly_chart(
                        fig_category,
                        use_container_width=True,
                        config={"displayModeBar": False}
                    )

            # ==================================
            # ROW — Payment Status Doughnut | Top 10 Customers
            # ==================================

            col3, col4 = st.columns(2)

            with col3:

                with st.container():
                    st.markdown("##### Payment Status")

                    payment_status_counts = (
                        filtered_df
                        .groupby("payment_status")
                        .size()
                        .reset_index(name="count")
                )

                    fig_status = px.pie(
                        payment_status_counts,
                        values="count",
                        names="payment_status",
                        hole=0.6,
                        color="payment_status",
                        color_discrete_map=STATUS_COLOR_MAP,
                    )

                    fig_status.update_traces(
                        textinfo="percent",
                        textfont=dict(size=13, color="#000000"),
                    )

                    fig_status.update_layout(

                        margin=dict(
                            t=10,
                            b=10,
                            l=10,
                            r=10
                        ),

                        showlegend=True,

                        legend=dict(
                            font=dict(
                                size=12,
                                color="#000000"
                            ),
                            orientation="h",
                            y=-0.1
                        ),

                        plot_bgcolor=CARD_BG,

                        paper_bgcolor=CARD_BG,

                        height=210

                    )

                    st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})


            with col4:

                with st.container():
                    st.markdown("##### Top 10 Customers")

                    top_customers = (
                        filtered_df
                        .groupby("customer")["total_amount"]
                        .sum()
                        .reset_index()
                        .sort_values("total_amount", ascending=False)
                        .head(10)
                    )

                    fig_top = px.bar(
                        top_customers,
                        x="total_amount",
                        y="customer",
                        orientation="h",
                        text="total_amount",
                        color_discrete_sequence=[COLOR_SEQUENCE[2]],
                    )

                    fig_top.update_traces(
                        texttemplate="%{text:,.0f}",
                        textposition="outside",
                        textfont=dict(size=12, color="#000000"),
                        cliponaxis=False,
                    )

                    fig_top.update_layout(
                        margin=dict(t=10, b=10, l=10, r=80),
                        yaxis=dict(autorange="reversed"),
                        xaxis_title=None,
                        yaxis_title=None,
                    )
                    _dark_chart_layout(fig_top, height=210)

                    st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})

            # ==================================
            # RECENT INVOICES — compact table
            # ==================================

            with st.container(border=True):

                st.markdown("##### Recent Invoices")

                recent_invoices = (
                    filtered_df[
                        [
                            "invoice_id",
                            "customer",
                            "invoice_date",
                            "total_amount",
                            "payment_status"
                        ]
                    ]
                    .drop_duplicates(subset="invoice_id")
                    .sort_values("invoice_date", ascending=False)
                    .head(15)
                )

                st.dataframe(
                    recent_invoices,
                    use_container_width=True,
                    height=560,
                    hide_index=True,
                )

            # ==================================
            # CSV EXPORT
            # ==================================

            if export_csv_clicked:

                csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="📥 Download Filtered Data (CSV)",
                    data=csv_bytes,
                    file_name="dashboard_export.csv",
                    mime="text/csv",
                )

            # ==================================
            # PDF EXPORT (Full visual report)
            # ==================================

            if export_pdf_clicked:

                with st.spinner("Building PDF report..."):

                    from src.dashboard_report import generate_dashboard_pdf

                    kpis = {
                        "registered_customers": registered_customers,
                        "purchasing_customers": purchasing_customers,
                        "total_invoices": total_invoices,
                        "paid_invoices": paid_invoices,
                        "total_revenue": total_revenue,
                        "amount_collected": amount_collected,
                        "collection_rate": collection_rate,
                        "outstanding_balance": outstanding_balance,
                    }

                    charts = {
                        "Monthly Revenue Trend": fig_trend,
                        "Yearly Revenue": fig_yearly,
                        "Revenue By Category": fig_category,
                        "Payment Status": fig_status,
                        "Top 10 Customers": fig_top,
                    }

                    pdf_path = generate_dashboard_pdf(
                        kpis=kpis,
                        charts=charts,
                        recent_invoices=recent_invoices,
                    )

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Dashboard Report (PDF)",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                    )

        else:

            st.warning("No invoice data available.")

    else:

        st.warning("No processed invoice dataset found.")

# ==================================================
# DATASET VIEWER
# ==================================================

elif menu == "📁 Data Explorer":

    st.header(
        "Processed Invoice Dataset"
    )

    if os.path.exists(
        PROCESSED_INVOICES_FILE
    ):

        df = pd.read_excel(
            PROCESSED_INVOICES_FILE
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        st.metric(
            "Total Records",

            len(df)
        )

    else:

        st.warning(
            "No processed invoice dataset found."
        )