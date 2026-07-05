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
    else:
        customers = pd.DataFrame(
            customers,
            columns=["id", "name", "phone", "email", "company", "status"]
        )

    customer_map = {}

    if not customers.empty:
        for row in customers.itertuples():
            customer_map[row.id] = f"{row.name} ({row.company})"

    # ---------------- SAFE SESSION STATE ----------------
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []

    # ---------------- ADD ITEM SECTION ----------------
    with st.expander("➕ Add Items"):

        col1, col2, col3 = st.columns(3)

        with col1:
            item_name = st.text_input("Item Name", key="item_name")

        with col2:
            qty = st.number_input("Qty", min_value=1, step=1, key="qty")

        with col3:
            price = st.number_input("Price", min_value=0.0, key="price")

        if st.button("➕ Add Item", key="add_item_btn"):

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
    st.subheader("🧾 Quotation Items")

    subtotal = 0

    if st.session_state.quote_items:

        for i, item in enumerate(st.session_state.quote_items):

            c1, c2, c3, c4, c5 = st.columns([3,1,2,2,1])

            c1.write(item["item"])
            c2.write(item["qty"])
            c3.write(item["price"])
            c4.write(item["total"])

            subtotal += item["total"]

            if c5.button("❌", key=f"del_item_{i}"):

                st.session_state.quote_items.pop(i)
                st.rerun()

    else:
        st.info("No items added yet")

    st.markdown("---")

    # ---------------- CUSTOMER ----------------
    if not customer_map:
        st.warning("No customers found")
        return

    customer_id = st.selectbox(
        "Select Customer",
        list(customer_map.keys()),
        format_func=lambda x: customer_map[x],
        key="customer_select"
    )

    discount = st.number_input("Discount (%)", 0.0, 100.0, key="discount")
    tax = st.number_input("Tax (%)", 0.0, 100.0, key="tax")
    status = st.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"], key="status")

    # ---------------- VERSION ----------------
    version = f"V{len(df) + 1}"
    st.info(f"📌 Version: {version}")

    # ---------------- CALCULATION ----------------
    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)

    st.success(f"Subtotal: {subtotal:.2f}")
    st.success(f"Total: {total:.2f}")

    # ---------------- SAVE QUOTATION ----------------
    if st.button("💾 Save Quotation", key="save_quote"):

        if not st.session_state.quote_items:
            st.error("Add at least one item")
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

    # ---------------- LIST QUOTATIONS ----------------
    st.markdown("---")
    st.subheader("📑 All Quotations")

    if df.empty:
        st.info("No quotations found")
        return

    for row in df.itertuples():

        with st.expander(f"{row.customer_name} | {row.version} | {row.total}"):

            st.write("Status:", row.status)
            st.write("Date:", row.created_on)
            st.write("Total:", row.total)

            st.write("Items:")

            try:
                items = json.loads(row.items)
                st.table(pd.DataFrame(items))
            except:
                st.error("Invalid item data")
