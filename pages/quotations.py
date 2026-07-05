import streamlit as st
import pandas as pd
import json
from datetime import date

from database import (
    add_quotation,
    get_quotations,
    get_customers,
    delete_quotation,
    update_quotation
)

from utils.pdf_generator import generate_quotation_pdf


def quotations_page():

    st.title("📄 Quotations")

    # ---------------- SESSION INIT ----------------
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

    # ---------------- EDIT MODE ----------------
    if "edit_quote" in st.session_state:

        qid = st.session_state.edit_quote
        row = df[df["id"] == qid].iloc[0]

        st.subheader("✏️ Edit Quotation")

        edit_customer = st.text_input("Customer Name", value=row["customer_name"])

        edit_status = st.selectbox(
            "Status",
            ["Draft", "Sent", "Approved", "Rejected"],
            index=["Draft", "Sent", "Approved", "Rejected"].index(row["status"]),
            key="edit_status"
        )

        if st.button("Update Quotation", key="update_btn"):

            update_quotation(
                qid,
                edit_customer,
                json.loads(row["items"]),
                row["subtotal"],
                row["discount"],
                row["tax"],
                row["total"],
                edit_status
            )

            del st.session_state.edit_quote
            st.success("Quotation updated successfully!")
            st.rerun()

        st.markdown("---")

    # ---------------- CREATE QUOTATION ----------------
    with st.expander("➕ Create Quotation"):

        if not customer_map:
            st.warning("No customers found")
            return

        customer_id = st.selectbox(
            "Select Customer",
            list(customer_map.keys()),
            format_func=lambda x: customer_map[x],
            key="customer_select"
        )

        # ---------------- ITEM INPUT ----------------
        st.subheader("Add Items")

        col1, col2, col3 = st.columns(3)

        with col1:
            item_name = st.text_input("Item Name", key="item_name")

        with col2:
            qty = st.number_input("Qty", min_value=1, step=1, key="qty")

        with col3:
            price = st.number_input("Price", min_value=0.0, step=10.0, key="price")

        if st.button("Add Item", key="add_item"):

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

        # ---------------- ITEMS DISPLAY ----------------
        subtotal = 0

        if st.session_state.quote_items:
            st.subheader("🧾 Items")

            for i, item in enumerate(st.session_state.quote_items):
                col1, col2, col3, col4 = st.columns(4)

                col1.write(item["item"])
                col2.write(item["qty"])
                col3.write(item["price"])
                col4.write(item["total"])

                subtotal += item["total"]

        else:
            st.info("No items added yet")

        st.markdown("---")

        # ---------------- DISCOUNT / TAX ----------------
        col1, col2, col3 = st.columns(3)

        with col1:
            discount = st.number_input("Discount (%)", 0.0, 100.0, 0.0, key="discount")

        with col2:
            tax = st.number_input("Tax (%)", 0.0, 100.0, 0.0, key="tax")

        with col3:
            status = st.selectbox(
                "Status",
                ["Draft", "Sent", "Approved", "Rejected"],
                key="status"
            )

        # ---------------- VERSION ----------------
        df = get_quotations()
        existing = df[df["customer_name"] == customer_map.get(customer_id, "")]
        version = f"V{len(existing) + 1}"

        st.info(f"📌 Version: {version}")

        # ---------------- TOTAL ----------------
        after_discount = subtotal - (subtotal * discount / 100)
        total = after_discount + (after_discount * tax / 100)

        st.success(f"Subtotal: {subtotal:.2f}")
        st.success(f"Total: {total:.2f}")

        # ---------------- SAVE ----------------
        if st.button("💾 Save Quotation", key="save_quote"):

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

    # ---------------- LIST QUOTATIONS ----------------
    st.markdown("---")
    st.subheader("📑 All Quotations")

    df = get_quotations()

    if df.empty:
        st.info("No quotations found")

    else:

        for row in df.itertuples():

            with st.expander(f"#{row.id} | {row.customer_name} | {row.total}"):

                col1, col2 = st.columns(2)

                with col1:
                    st.write("📅 Date:", row.created_on)
                    st.write("📌 Version:", row.version)
                    st.write("💰 Total:", row.total)
                    st.write("📊 Status:", row.status)

                # ---------------- ITEMS ----------------
                st.write("🧾 Items")

                try:
                    items = json.loads(row.items)
                    st.table(pd.DataFrame(items))
                except:
                    st.error("Invalid items data")

                # ---------------- ACTIONS ----------------
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("✏️ Edit", key=f"edit_{row.id}"):
                        st.session_state.edit_quote = row.id
                        st.rerun()

                with col2:
                    if st.button("🗑️ Delete", key=f"del_{row.id}"):
                        delete_quotation(row.id)
                        st.success("Deleted successfully")
                        st.rerun()

                with col3:
                    if st.button("📥 PDF", key=f"pdf_{row.id}"):

                        pdf_path = generate_quotation_pdf(
                            row.customer_name,
                            json.loads(row.items),
                            row.subtotal,
                            row.discount,
                            row.tax,
                            row.total,
                            row.created_on,
                            row.version
                        )

                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "Download PDF",
                                f,
                                file_name=f"quotation_{row.id}.pdf",
                                key=f"dl_{row.id}"
                            )
