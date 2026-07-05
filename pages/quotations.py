import streamlit as st
import pandas as pd
from datetime import date

from database import add_quotation, get_quotations, get_customers


# ================= HELPERS =================
def calculate_total(items, discount, tax):
    subtotal = sum(i["qty"] * i["price"] for i in items)
    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)
    return subtotal, total


# ================= PAGE =================
def quotations_page():

    st.title("💼 Quotations")

    # ---------------- SESSION ----------------
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []

    if "edit_quote_id" not in st.session_state:
        st.session_state.edit_quote_id = None

    df = get_quotations()
    if df is None:
        df = pd.DataFrame()

    customers = get_customers()
    customers = pd.DataFrame(
        customers,
        columns=["id", "name", "phone", "email", "company", "status"]
    )

    customer_map = {
        row.id: f"{row.name} ({row.company})"
        for row in customers.itertuples()
    }

    # ================= CREATE / EDIT FORM =================
    st.subheader("➕ Create / Edit Quotation")

    if not customer_map:
        st.warning("No customers found")
        return

    customer_id = st.selectbox(
        "Customer",
        list(customer_map.keys()),
        format_func=lambda x: customer_map[x],
        key="customer_select"
    )

    # -------- ITEM INPUT --------
    st.markdown("### Add Items")

    col1, col2, col3 = st.columns(3)

    with col1:
        item_name = st.text_input("Item Name", key="item_name")

    with col2:
        qty = st.number_input("Qty", min_value=1, step=1, key="qty")

    with col3:
        price = st.number_input("Price", min_value=0.0, step=10.0, key="price")

    if st.button("➕ Add Item", key="add_item"):

        if item_name.strip():
            st.session_state.quote_items.append({
                "item": item_name,
                "qty": qty,
                "price": price
            })
            st.rerun()
        else:
            st.error("Enter item name")

    # -------- SHOW ITEMS (EDITABLE) --------
    subtotal = 0

    if st.session_state.quote_items:
        st.markdown("### Items")

        for i, item in enumerate(st.session_state.quote_items):

            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])

            item["item"] = c1.text_input("Item", item["item"], key=f"item_{i}")
            item["qty"] = c2.number_input("Qty", value=item["qty"], key=f"qty_{i}")
            item["price"] = c3.number_input("Price", value=item["price"], key=f"price_{i}")

            item_total = item["qty"] * item["price"]
            c4.write(item_total)

            if c5.button("🗑", key=f"del_{i}"):
                st.session_state.quote_items.pop(i)
                st.rerun()

            subtotal += item_total
    else:
        st.info("No items added yet")

    st.markdown("---")

    # -------- DISCOUNT / TAX --------
    col1, col2, col3 = st.columns(3)

    discount = col1.number_input("Discount (%)", 0.0, 100.0, 0.0, key="discount")
    tax = col2.number_input("Tax (%)", 0.0, 100.0, 0.0, key="tax")
    status = col3.selectbox(
        "Status",
        ["Draft", "Sent", "Approved", "Rejected"],
        key="status"
    )

    subtotal, total = calculate_total(
        st.session_state.quote_items,
        discount,
        tax
    )

    st.success(f"Subtotal: {subtotal:.2f}")
    st.success(f"Total: {total:.2f}")

    # ================= SAVE =================
    if st.button("💾 Save Quotation"):

        if not st.session_state.quote_items:
            st.error("Add items first")
            return

        add_quotation(
            customer_map[customer_id],
            st.session_state.quote_items,
            subtotal,
            discount,
            tax,
            total,
            status,
            str(date.today()),
            "V1"
        )

        st.session_state.quote_items = []
        st.success("Saved successfully!")
        st.rerun()

    # ================= LIST =================
    st.markdown("---")
    st.subheader("📄 All Quotations")

    df = get_quotations()

    if df.empty:
        st.info("No quotations found")

    else:

        for _, row in df.iterrows():

            with st.container():
                st.markdown(f"""
                ### {row['customer_name']} | {row['version']}
                **Total:** {row['total']}  
                **Status:** {row['status']}  
                **Date:** {row['created_on']}
                """)

                col1, col2 = st.columns(2)

                # -------- DELETE --------
                if col1.button("🗑 Delete", key=f"del_quote_{row['id']}"):
                    import sqlite3
                    conn = sqlite3.connect("crm.db")
                    cur = conn.cursor()
                    cur.execute("DELETE FROM quotations WHERE id=?", (row["id"],))
                    conn.commit()
                    conn.close()
                    st.rerun()

                # -------- EDIT --------
                if col2.button("✏ Edit", key=f"edit_quote_{row['id']}"):
                    st.session_state.quote_items = eval(row["items"])  # load items
                    st.session_state.edit_quote_id = row["id"]
                    st.rerun()

                st.markdown("---")
