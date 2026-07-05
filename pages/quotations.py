import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers


DB_NAME = "crm.db"


# ================= UPDATE =================
def update_quotation(qid, customer_name, items, subtotal, discount, tax, total, status, version):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE quotations
        SET customer_name=?, items=?, subtotal=?, discount=?, tax=?, total=?, status=?, version=?
        WHERE id=?
    """, (
        customer_name,
        json.dumps(items),
        subtotal,
        discount,
        tax,
        total,
        status,
        version,
        qid
    ))

    conn.commit()
    conn.close()


# ================= DELETE =================
def delete_quotation(qid):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM quotations WHERE id=?", (qid,))
    conn.commit()
    conn.close()


# ================= PAGE =================
def quotations_page():

    st.title("💼 Quotations")

    # ---------------- SESSION ----------------
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []

    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None

    df = get_quotations()

    customers = get_customers()
    customers = pd.DataFrame(
        customers,
        columns=["id", "name", "phone", "email", "company", "status"]
    )

    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers.itertuples()}

    # ======================================================
    # 🟢 EDIT MODE (IMPORTANT FIX)
    # ======================================================
    if st.session_state.edit_id:

        st.subheader("✏ Edit Quotation Mode")

        edit_row = df[df["id"] == st.session_state.edit_id].iloc[0]
        edit_items = json.loads(edit_row["items"])

        # overwrite session items ONCE
        if "edit_loaded" not in st.session_state:
            st.session_state.quote_items = edit_items
            st.session_state.edit_loaded = True

        customer_id = st.selectbox(
            "Customer",
            list(customer_map.keys()),
            index=list(customer_map.keys()).index(
                [k for k, v in customer_map.items() if v == edit_row["customer_name"]][0]
            ),
            key="edit_customer"
        )

        status = st.selectbox(
            "Status",
            ["Draft", "Sent", "Approved", "Rejected"],
            index=["Draft", "Sent", "Approved", "Rejected"].index(edit_row["status"]),
            key="edit_status"
        )

    else:
        st.subheader("➕ Create Quotation")

        customer_id = st.selectbox(
            "Customer",
            list(customer_map.keys()),
            format_func=lambda x: customer_map[x],
            key="create_customer"
        )

        status = st.selectbox(
            "Status",
            ["Draft", "Sent", "Approved", "Rejected"],
            key="create_status"
        )

    # ======================================================
    # ITEMS (FIXED KEYS - NO DUPLICATE ERROR)
    # ======================================================
    st.markdown("### Items")

    c1, c2, c3 = st.columns(3)

    item_name = c1.text_input("Item", key="item_name")
    qty = c2.number_input("Qty", 1, key="qty")
    price = c3.number_input("Price", 0.0, key="price")

    if st.button("➕ Add Item", key="add_item"):
        st.session_state.quote_items.append({
            "item": item_name,
            "qty": qty,
            "price": price
        })
        st.rerun()

    subtotal = 0

    # ======================================================
    # ITEM LIST (ALL KEYS FIXED)
    # ======================================================
    for i, it in enumerate(st.session_state.quote_items):

        cols = st.columns([3, 2, 2, 1])

        it["item"] = cols[0].text_input("Item", it["item"], key=f"item_{i}")
        it["qty"] = cols[1].number_input("Qty", it["qty"], key=f"qty_{i}")
        it["price"] = cols[2].number_input("Price", it["price"], key=f"price_{i}")

        subtotal += it["qty"] * it["price"]

        if cols[3].button("🗑", key=f"del_{i}"):
            st.session_state.quote_items.pop(i)
            st.rerun()

    st.markdown("---")

    # ======================================================
    # CALCULATION
    # ======================================================
    discount = st.number_input("Discount %", 0.0, 100.0, key="discount")
    tax = st.number_input("Tax %", 0.0, 100.0, key="tax")

    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)

    st.success(f"Subtotal: {subtotal:.2f}")
    st.success(f"Total: {total:.2f}")

    # ======================================================
    # SAVE / UPDATE (FIXED)
    # ======================================================
    if st.button("💾 Save"):

        customer_name = customer_map[customer_id]

        if st.session_state.edit_id:

            update_quotation(
                st.session_state.edit_id,
                customer_name,
                st.session_state.quote_items,
                subtotal,
                discount,
                tax,
                total,
                status,
                "V-EDIT"
            )

            st.success("Updated successfully!")
            st.session_state.edit_id = None
            st.session_state.edit_loaded = False

        else:

            add_quotation(
                customer_name,
                st.session_state.quote_items,
                subtotal,
                discount,
                tax,
                total,
                status,
                str(date.today()),
                "V1"
            )

            st.success("Saved successfully!")

        st.session_state.quote_items = []
        st.rerun()

    # ======================================================
    # LIST (NO ERRORS)
    # ======================================================
    st.markdown("---")
    st.subheader("All Quotations")

    df = get_quotations()

    for _, row in df.iterrows():

        st.markdown(f"""
        ### {row['customer_name']}
        **Total:** {row['total']} | **Status:** {row['status']}
        """)

        c1, c2 = st.columns(2)

        if c1.button("✏ Edit", key=f"edit_{row['id']}"):
            st.session_state.edit_id = row["id"]
            st.session_state.quote_items = json.loads(row["items"])
            st.session_state.edit_loaded = False
            st.rerun()

        if c2.button("🗑 Delete", key=f"delq_{row['id']}"):
            delete_quotation(row["id"])
            st.rerun()

        st.markdown("---")
