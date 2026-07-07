import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf

DB_NAME = "crm.db"

# ================= UPDATE =================
def update_quotation(qid, customer_name, items, subtotal, discount, tax, total, status, version):
    with sqlite3.connect(DB_NAME) as conn:
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

# ================= DELETE =================
def delete_quotation(qid):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM quotations WHERE id=?", (qid,))

# ================= PAGE =================
def quotations_page():
    st.title("💼 Quotations")

    # Initialize session state
    st.session_state.setdefault("quote_items", [])
    st.session_state.setdefault("edit_id", None)
    st.session_state.setdefault("edit_loaded", False)
    st.session_state.setdefault("edit_customer", None)
    st.session_state.setdefault("edit_status", "Draft")

    df = get_quotations()
    customers = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers.itertuples()}
    customer_options = list(customer_map.keys())

    # Create new quotation logic
    if st.button("➕ Create New Quotation"):
        st.session_state.quote_items = []
        st.session_state.edit_id = None
        st.session_state.edit_loaded = False
        st.session_state.edit_customer = None
        st.session_state.edit_status = "Draft"
        st.rerun()  # <--- Use this instead

    # Load edit logic
    if st.session_state.edit_id and not st.session_state.edit_loaded:
        match = df[df["id"] == st.session_state.edit_id]
        if not match.empty:
            row = match.iloc[0]
            try:
                st.session_state.quote_items = json.loads(row["items"])
            except json.JSONDecodeError:
                st.session_state.quote_items = []
            st.session_state.edit_customer = row["customer_name"]
            st.session_state.edit_status = row["status"]
        st.session_state.edit_loaded = True

    # Mode indication
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")

    default_customer = customer_options[0]
    if st.session_state.edit_id:
        default_customer = next(
            (k for k, v in customer_map.items()
             if v == st.session_state.edit_customer),
            customer_options[0]
        )

    # Customer selection
    customer_id = st.selectbox(
        "Customer",
        customer_options,
        index=customer_options.index(default_customer),
        format_func=lambda x: customer_map[x],
        key="customer_select"
    )

    # Status selection
    status = st.selectbox(
        "Status",
        ["Draft", "Sent", "Approved", "Rejected"],
        index=(
            ["Draft", "Sent", "Approved", "Rejected"].index(st.session_state.edit_status)
            if st.session_state.edit_status in ["Draft", "Sent", "Approved", "Rejected"]
            else 0
        ),
        key="status_select"
    )

    # Item input
    st.markdown("### Items")
    item_input = st.text_input("Item", key="item_input")
    qty_input = st.number_input("Qty", value=1.0, key="qty_input")
    price_input = st.number_input("Price", value=0.0, key="price_input")

    if st.button("➕ Add Item"):
        st.session_state.quote_items.append({
            "item": item_input,
            "qty": qty_input,
            "price": price_input
        })
        st.rerun()

    # Item list display
    subtotal = 0
    updated_items = []

    for i, it in enumerate(st.session_state.quote_items):
        cols = st.columns([3, 2, 2, 1])
        new_item = cols[0].text_input("Item", it["item"], key=f"it_{i}")
        new_qty = cols[1].number_input("Qty", value=float(it["qty"]), key=f"qt_{i}")
        new_price = cols[2].number_input("Price", value=float(it["price"]), key=f"pr_{i}")

        subtotal += new_qty * new_price

        if cols[3].button("❌", key=f"rm_{i}"):
            continue

        updated_items.append({
            "item": new_item,
            "qty": new_qty,
            "price": new_price
        })

    st.session_state.quote_items = updated_items

    st.markdown("---")

    # Totals
    discount = st.number_input("Discount %", value=0.0, key="discount")
    tax = st.number_input("Tax %", value=0.0, key="tax")

    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)

    st.success(f"Subtotal: {subtotal:.2f}")
    st.success(f"Total: {total:.2f}")

    # Save logic with duplicate check
    if st.button("💾 Save Quotation"):
        customer_name = customer_map[customer_id]

        # Check for duplicate quotation
        existing_quotations = df[(df['customer_name'] == customer_name) & (df['items'] == json.dumps(st.session_state.quote_items))]
        if not existing_quotations.empty:
            st.error("This quotation already exists!")
        else:
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

            # Clear the session state for a fresh start
            st.session_state.quote_items = []
            st.session_state.edit_id = None
            st.session_state.edit_loaded = False
            st.session_state.edit_customer = None
            st.session_state.edit_status = "Draft"
            st.experimental_rerun()

    # List all quotations nicely
    st.markdown("---")
    st.subheader("All Quotations")

    for _, row in df.iterrows():
        st.markdown(f"""
        ### {row['customer_name']}
        **Total:** {row['total']} | **Status:** {row['status']}
        """)

        c1, c2, c3 = st.columns(3)

        if c1.button("✏ Edit", key=f"e_{row['id']}"):
            st.session_state.edit_id = row["id"]
            st.session_state.edit_loaded = False
            st.rerun()

        if c2.button("🗑 Delete", key=f"d_{row['id']}"):
            delete_quotation(row["id"])
            st.experimental_rerun()

        # PDF Generation
        safe_row = row.to_dict()
        items = safe_row.get("items", [])

        if isinstance(items, str):
            try:
                items = json.loads(items)
            except json.JSONDecodeError:
                items = []

        safe_row["items"] = items

        pdf_buffer = generate_quotation_pdf(safe_row)

        c3.download_button(
            label="📄 PDF",
            data=pdf_buffer,
            file_name=f"quotation_{row['id']}.pdf",
            mime="application/pdf",
            key=f"pdf_{row['id']}"
        )

        st.markdown("---")
