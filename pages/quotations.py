import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf

DB_NAME = "crm.db"

# ================= DATABASE FUNCTIONS =================
def update_quotation(qid, customer_name, items, subtotal, discount, tax, total, status, version):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        UPDATE quotations
        SET customer_name=?, items=?, subtotal=?, discount=?, tax=?, total=?, status=?, version=?
        WHERE id=?
    """, (customer_name, json.dumps(items), subtotal, discount, tax, total, status, version, qid))
    conn.commit()
    conn.close()

def delete_quotation(qid):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM quotations WHERE id=?", (qid,))
    conn.commit()
    conn.close()

# ================= PAGE =================
def quotations_page():
    st.title("💼 Quotations")

    # --- Session Init ---
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False
    if "edit_customer" not in st.session_state: st.session_state.edit_customer = None
    if "edit_status" not in st.session_state: st.session_state.edit_status = "Draft"

    def reset_all_states():
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False
        st.session_state.edit_customer = None
        st.session_state.edit_status = "Draft"

    # --- Data ---
    df = get_quotations()
    customers_df = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers_df.itertuples()}
    customer_options = list(customer_map.keys())

    # --- Create New ---
    if st.button("➕ Create New Quotation"):
        reset_all_states()
        st.rerun()

    # --- Edit Load Logic ---
    if st.session_state.edit_id and not st.session_state.edit_loaded:
        match = df[df["id"] == st.session_state.edit_id]
        if not match.empty:
            row = match.iloc[0]
            st.session_state.quote_items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            st.session_state.edit_customer = row["customer_name"]
            st.session_state.edit_status = row["status"]
        st.session_state.edit_loaded = True

    # --- UI: Entry Form ---
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")

    default_customer = customer_options[0]
    if st.session_state.edit_id:
        default_customer = next((k for k, v in customer_map.items() if v == st.session_state.edit_customer), customer_options[0])

    customer_id = st.selectbox("Customer", customer_options, index=customer_options.index(default_customer), format_func=lambda x: customer_map[x], key="customer_select")
    status = st.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"], index=["Draft", "Sent", "Approved", "Rejected"].index(st.session_state.edit_status) if st.session_state.edit_status in ["Draft", "Sent", "Approved", "Rejected"] else 0, key="status_select")

    st.markdown("### Items")
    item_input = st.text_input("Item", key="item_input")
    qty_input = st.number_input("Qty", value=1.0, key="qty_input")
    price_input = st.number_input("Price", value=0.0, key="price_input")

    if st.button("➕ Add Item"):
        st.session_state.quote_items.append({"item": item_input, "qty": qty_input, "price": price_input})
        st.rerun()

    # --- Item List ---
    subtotal = 0
    updated_items = []
    for i, it in enumerate(st.session_state.quote_items):
        cols = st.columns([3, 2, 2, 1])
        n_item = cols[0].text_input("Item", it["item"], key=f"it_{i}")
        n_qty = cols[1].number_input("Qty", value=float(it["qty"]), key=f"qt_{i}")
        n_prc = cols[2].number_input("Price", value=float(it["price"]), key=f"pr_{i}")
        subtotal += n_qty * n_prc
        if cols[3].button("❌", key=f"rm_{i}"):
            st.session_state.quote_items.pop(i)
            st.rerun()
        updated_items.append({"item": n_item, "qty": n_qty, "price": n_prc})
    
    st.session_state.quote_items = updated_items

    # --- Totals ---
    st.markdown("---")
    discount = st.number_input("Discount %", value=0.0, key="discount")
    tax = st.number_input("Tax %", value=0.0, key="tax")
    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)
    st.success(f"Subtotal: {subtotal:.2f} | Total: {total:.2f}")

    # --- Save / Cancel Actions ---
    col1, col2 = st.columns([1, 6])
    if col1.button("💾 Save"):
        cust_name = customer_map[customer_id]
        if st.session_state.edit_id:
            update_quotation(st.session_state.edit_id, cust_name, st.session_state.quote_items, subtotal, discount, tax, total, status, "V-EDIT")
        else:
            add_quotation(cust_name, st.session_state.quote_items, subtotal, discount, tax, total, status, str(date.today()), "V1")
        
        reset_all_states()
        st.rerun()
        
    if col2.button("❌ Cancel"):
        reset_all_states()
        st.rerun()

    # --- List View ---
    st.markdown("---")
    st.subheader("All Quotations")
    df = get_quotations()
    for _, row in df.iterrows():
        st.markdown(f"### {row['customer_name']} - {row['status']} - Total: {row['total']:.2f}")
        c1, c2, c3 = st.columns(3)
        if c1.button("✏ Edit", key=f"e_{row['id']}"):
            st.session_state.edit_id = row["id"]
            st.session_state.edit_loaded = False
            st.rerun()
        if c2.button("🗑 Delete", key=f"d_{row['id']}"):
            delete_quotation(row["id"])
            st.rerun()
        
        items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
        c3.download_button("📄 PDF", data=generate_quotation_pdf({**row.to_dict(), "items": items}), file_name=f"q_{row['id']}.pdf", key=f"pdf_{row['id']}")
