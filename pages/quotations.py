import streamlit as st
import pandas as pd
from datetime import date
import json

from utils.pdf_generator import generate_quotation_pdf
from database import add_quotation, get_quotations, get_customers


def quotations_page():

    st.title("💼 Quotations")

    # ---------------- INIT SESSION ----------------
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []

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
        subtotal = sum(i["total"] for i in st.session_state.quote_items)

        if st.session_state.quote_items:
            st.subheader("🧾 Items")

            for item in st.session_state.quote_items:
                col1, col2, col3, col4 = st.columns(4)

                col1.write(item["item"])
                col2.write(item["qty"])
                col3.write(item["price"])
                col4.write(item["total"])
        else:
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
        df = get_quotations()
        existing_versions = df[df["customer_name"] == customer_map.get(customer_id, "")]
        version = f"V{len(existing_versions) + 1}"

        st.info(f"📌 Version: {version}")

        # ---------------- TOTAL ----------------
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

    # ---------------- LIST SECTION ----------------
    st.markdown("---")
    st.subheader("All Quotations")

    df = get_quotations()

    if df.empty:
        st.info("No quotations found")
    else:
        for row in df.itertuples():

            with st.expander(f"{row.customer_name} | {row.version} | {row.total}"):

                st.write("Status:", row.status)
                st.write("Date:", row.created_on)
                st.write("Subtotal:", row.subtotal)
                st.write("Discount:", row.discount)
                st.write("Tax:", row.tax)
                st.write("Total:", row.total)

                # ITEMS
                try:
                    items = json.loads(row.items)
                    st.table(pd.DataFrame(items))
                except:
                    st.error("Invalid item data")

                # ---------------- PDF DOWNLOAD ----------------
                pdf_data = {
                    "customer_name": row.customer_name,
                    "items": json.loads(row.items),
                    "subtotal": row.subtotal,
                    "discount": row.discount,
                    "tax": row.tax,
                    "total": row.total
                }

                pdf_file = generate_quotation_pdf(pdf_data)

                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_file,
                    file_name=f"Quotation_{row.version}.pdf",
                    mime="application/pdf"
                )
