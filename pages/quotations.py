import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers


DB_NAME = "crm.db"


# ================= UPDATE QUOTATION =================
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

    # ---------------- DATA ----------------
    df = get_quotations()

    customers = get_customers()
    customers = pd.DataFrame(
        customers,
        columns=["id", "name", "phone", "email", "company", "status"]
    )

    customer_map = {
        r.id: f"{r.name} ({r.company})"
        for r in customers.itertuples()
    }

    # ================= FORM =================
    st.subheader("Create / Edit Quotation")

    customer_id = st.selectbox(
        "Customer",
        list(customer_map.keys()),
        format_func=lambda x: customer_map[x],
        key="customer"
    )

    # ---------- ITEMS ----------
    st.markdown("### Items")

    c1, c2, c3 = st.columns(3)

    item = c1.text_input("Item", key="item")
    qty = c2.number_input("Qty", 1, step=1, key="qty")
    price = c3.number_input("Price", 0.0, step=10.0, key="price")

    if st.button("Add Item"):
        st.session_state.quote_items.append({
            "item": item,
            "qty": qty,
            "price": price
        })
        st.rerun()

    subtotal = 0

    # ---------- ITEM LIST ----------
    for i, it in enumerate(st.session_state.quote_items):

        cols = st.columns([3,2,2,1])

        it["item"] = cols[0].text_input("Item", it["item"], key=f"it{i}")
        it["qty"] = cols[1].number_input("Qty", value=it["qty"], key=f"q{i}")
        it["price"] = cols[2].number_input("Price", value=it["price"], key=f"p{i}")

        subtotal += it["qty"] * it["price"]

        if cols[3].button("❌", key=f"del{i}"):
            st.session_state.quote_items.pop(i)
            st.rerun()

    st.markdown("---")

    # ---------- TAX ----------
    col1, col2, col3 = st.columns(3)

    discount = col1.number_input("Discount %", 0.0, 100.0, 0.0)
    tax = col2.number_input("Tax %", 0.0, 100.0, 0.0)
    status = col3.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)

    st.success(f"Subtotal: {subtotal:.2f}")
    st.success(f"Total: {total:.2f}")

    # ================= SAVE / UPDATE =================
    if st.button("💾 Save / Update"):

        if not st.session_state.quote_items:
            st.error("Add items first")
            return

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

            st.success("Quotation updated!")
            st.session_state.edit_id = None

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

            st.success("Quotation saved!")

        st.session_state.quote_items = []
        st.rerun()

    # ================= LIST =================
    st.markdown("---")
    st.subheader("All Quotations")

    df = get_quotations()

    for _, row in df.iterrows():

        with st.container():
            st.markdown(f"""
            ### {row['customer_name']} ({row['version']})
            **Total:** {row['total']}  
            **Status:** {row['status']}  
            **Date:** {row['created_on']}
            """)

            c1, c2, c3 = st.columns(3)

            # ---------- EDIT ----------
            if c1.button("✏ Edit", key=f"e{row['id']}"):

                st.session_state.quote_items = json.loads(row["items"])
                st.session_state.edit_id = row["id"]
                st.rerun()

            # ---------- DELETE ----------
            if c2.button("🗑 Delete", key=f"d{row['id']}"):
                delete_quotation(row["id"])
                st.rerun()

            # ---------- PDF ----------
            if c3.button("📄 PDF", key=f"p{row['id']}"):

                from utils.pdf_generator import generate_quotation_pdf

                pdf_path = generate_quotation_pdf(row)
                st.success("PDF generated!")
                st.download_button(
                    "Download PDF",
                    open(pdf_path, "rb"),
                    file_name="quotation.pdf"
                )

            st.markdown("---")
