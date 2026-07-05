import streamlit as st
import pandas as pd
from datetime import date
import json

from database import add_quotation, get_quotations, get_customers


def quotations_page():

    st.title("💼 Quotations (Pro Version)")

    df = get_quotations()
    if df is None:
        df = pd.DataFrame()

    # ---------------- CUSTOMERS ----------------
    customers = get_customers()

    if customers is None:
        customers = pd.DataFrame()
    else:
        customers = pd.DataFrame(
            customers,
            columns=["id", "name", "phone", "email", "company", "status"]
        )

    customer_map = {}

    if not customers.empty:
        for row in customers.itertuples():
            customer_map[row.id] = f"{row.name} ({row.company})"

    # ---------------- SESSION ITEMS ----------------
    if "items" not in st.session_state:
        st.session_state.items = []

    # ---------------- ADD ITEMS ----------------
    with st.expander("➕ Add Items"):

        col1, col2, col3 = st.columns(3)

        with col1:
            item_name = st.text_input("Item Name")

        with col2:
            qty = st.number_input("Qty", min_value=1, step=1)

        with col3:
            price = st.number_input("Price", min_value=0.0)

        if st.button("Add Item"):

            if item_name:
                st.session_state.items.append({
                    "item": item_name,
                    "qty": qty,
                    "price": price,
                    "total": qty * price
                })

                st.success("Item added!")
                st.rerun()

    # ---------------- SHOW ITEMS ----------------
    if st.session_state.items:

        st.subheader("🧾 Quotation Items")

        subtotal = 0

        for i, item in enumerate(st.session_state.items):

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.write(item["item"])
            c2.write(item["qty"])
            c3.write(item["price"])
            c4.write(item["total"])

            subtotal += item["total"]

            if c5.button("❌", key=f"del_item_{i}"):

                st.session_state.items.pop(i)
                st.rerun()

    else:
        subtotal = 0

    st.markdown("---")

    # ---------------- CUSTOMER ----------------
    if not customer_map:
        st.warning("No customers available")
        return

    customer_id = st.selectbox(
        "Select Customer",
        list(customer_map.keys()),
        format_func=lambda x: customer_map[x]
    )

    discount = st.number_input("Discount (%)", 0.0, 100.0, 0.0)
    tax = st.number_input("Tax (%)", 0.0, 100.0, 0.0)
    status = st.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

    version = f"V{len(df) + 1}"

    st.info(f"📌 Version: {version}")

    # ---------------- CALCULATION ----------------
    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)

    st.success(f"Subtotal: {subtotal}")
    st.success(f"Total: {total}")

    # ---------------- SAVE ----------------
    if st.button("💾 Save Quotation"):

        customer_name = customer_map[customer_id]

        add_quotation(
            customer_name,
            st.session_state.items,
            subtotal,
            discount,
            tax,
            total,
            status,
            str(date.today()),
            version
        )

        st.session_state.items = []
        st.success("Quotation saved successfully!")
        st.rerun()

    # ---------------- LIST ----------------
    st.subheader("All Quotations")

    if df.empty:
        st.info("No quotations found")
        return

    for row in df.itertuples():

        with st.expander(f"{row.customer_name} - {row.version}"):

            st.write("Status:", row.status)
            st.write("Total:", row.total)
            st.write("Date:", row.created_on)

            st.write("Items:")

            try:
                items = json.loads(row.items)
                st.table(items)
            except:
                st.error("Invalid items data")
