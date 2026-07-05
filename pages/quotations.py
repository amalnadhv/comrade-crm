import streamlit as st
import pandas as pd
from datetime import date
import json

from database import add_quotation, get_quotations, get_customers


def quotations_page():

    st.title("💼 Quotations (Pro CRM)")

    # ---------------- LOAD QUOTATIONS ----------------
    df = get_quotations()
    if df is None:
        df = pd.DataFrame()

    # ---------------- LOAD CUSTOMERS ----------------
    customers = get_customers()

    if customers is None:
        customers = pd.DataFrame()

    # ---------------- HANDLE CUSTOMER DATA ----------------
    try:
        customer_map = {}
        if not customers.empty:
            for row in customers.itertuples():
                customer_map[row.id] = f"{row.name} ({row.company})"
    except:
        customer_map = {}

    # ---------------- SESSION STATE ----------------
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []

    # ---------------- ADD ITEMS ----------------
    st.subheader("➕ Add Items")

    col1, col2, col3 = st.columns(3)

    with col1:
        item_name = st.text_input("Item Name")

    with col2:
        qty = st.number_input("Qty", min_value=1, step=1)

    with col3:
        price = st.number_input("Price", min_value=0.0)

    if st.button("Add Item"):

        if item_name.strip():
            st.session_state.quote_items.append({
                "item": item_name,
                "qty": qty,
                "price": price,
                "total": qty * price
            })
            st.success("Item added!")
            st.rerun()
        else:
            st.error("Item name required")

    # ---------------- SHOW ITEMS ----------------
    st.subheader("🧾 Items")

    subtotal = 0

    if st.session_state.quote_items:

        for i, item in enumerate(st.session_state.quote_items):

            c1, c2, c3, c4, c5 = st.columns([3, 1, 2, 2, 1])

            c1.write(item["item"])
            c2.write(item["qty"])
            c3.write(item["price"])
            c4.write(item["total"])

            subtotal += item["total"]

            if c5.button("❌", key=f"del_{i}"):
                st.session_state.quote_items.pop(i)
                st.rerun()
    else:
        st.info("No items added yet")

    st.markdown("---")

    # ---------------- CUSTOMER SELECT ----------------
    if not customer_map:
        st.warning("No customers found in database")
        return

    customer_id = st.selectbox(
        "Select Customer",
        list(customer_map.keys()),
        format_func=lambda x: customer_map[x]
    )

    discount = st.number_input("Discount %", 0.0, 100.0)
    tax = st.number_input("Tax %", 0.0, 100.0)
    status = st.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

    version = f"V{len(df) + 1}"

    st.info(f"Version: {version}")

    # ---------------- CALCULATION ----------------
    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)

    st.success(f"Subtotal: {subtotal:.2f}")
    st.success(f"Total: {total:.2f}")

    # ---------------- SAVE ----------------
    if st.button("Save Quotation"):

        if not st.session_state.quote_items:
            st.error("Please add items first")
            return

        customer_name = customer_map[customer_id]

        add_quotation(
            customer_name,
            st.session_state.quote_items,
            subtotal,
            discount,
            tax,
            total,
            status,
            str(date.today()),
            version
        )

        st.session_state.quote_items = []
        st.success("Quotation saved successfully!")
        st.rerun()

    # ---------------- DISPLAY QUOTATIONS ----------------
    st.markdown("---")
    st.subheader("All Quotations")

    if df.empty:
        st.info("No quotations found")
        return

    for row in df.itertuples():

        with st.expander(f"{row.customer_name} | {row.version} | {row.total}"):

            st.write("Status:", row.status)
            st.write("Date:", row.created_on)
            st.write("Total:", row.total)

            try:
                items = json.loads(row.items)
                st.table(pd.DataFrame(items))
            except:
                st.error("Invalid item data")
