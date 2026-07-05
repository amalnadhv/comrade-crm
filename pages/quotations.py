import streamlit as st
import pandas as pd
from datetime import date

from database import add_quotation, get_quotations, get_customers


def quotations_page():

    st.title("💼 Quotations")

    # ---------------- INIT SESSION ----------------
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []

    # ---------------- LOAD DATA ----------------
    df = get_quotations()
    if df is None:
        df = pd.DataFrame()

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

    # ---------------- CREATE QUOTATION ----------------
    with st.expander("➕ Create Quotation"):

        if not customer_map:
            st.warning("No customers found")
            return

        customer_id = st.selectbox(
            "Select Customer",
            list(customer_map.keys()),
            format_func=lambda x: customer_map[x]
        )

        # ---------------- ITEM SECTION ----------------
        st.subheader("Add Items")

        col1, col2, col3 = st.columns(3)

        with col1:
            item_name = st.text_input("Item Name")

        with col2:
            qty = st.number_input("Qty", min_value=1, step=1)

        with col3:
            price = st.number_input("Price", min_value=0.0, step=10.0)

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
                st.error("Enter item name")

        # ---------------- SHOW ITEMS ----------------
        if st.session_state.quote_items:
            st.subheader("🧾 Items")

            subtotal = 0

            for i, item in enumerate(st.session_state.quote_items):
                col1, col2, col3, col4 = st.columns(4)

                col1.write(item["item"])
                col2.write(item["qty"])
                col3.write(item["price"])
                col4.write(item["total"])

                subtotal += item["total"]

        else:
            subtotal = 0
            st.info("No items added yet")

        st.markdown("---")

        # ---------------- DISCOUNT / TAX ----------------
        col1, col2, col3 = st.columns(3)

        with col1:
            discount = st.number_input("Discount (%)", 0.0, 100.0, 0.0)

        with col2:
            tax = st.number_input("Tax (%)", 0.0, 100.0, 0.0)

        with col3:
            status = st.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

        # ---------------- VERSION ----------------
        existing_versions = df[df["customer_name"] == customer_map.get(customer_id, "")]
        version = f"V{len(existing_versions) + 1}"

        st.info(f"📌 Version: {version}")

        # ---------------- TOTAL CALCULATION ----------------
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

    # ---------------- LIST ----------------
    st.markdown("---")
    st.subheader("All Quotations")

    if df.empty:
        st.info("No quotations found")
    else:
        st.dataframe(df, use_container_width=True)
