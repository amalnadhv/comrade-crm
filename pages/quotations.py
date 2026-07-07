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

    # Session Initialization
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False
    if "edit_customer" not in st.session_state: st.session_state.edit_customer = None
    if "edit_status" not in st.session_state: st.session_state.edit_status = "Draft"

    # Data
    df = get_quotations()
    customers = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers.itertuples()}
    customer_options = list(customer_map.keys())

    # Create New Logic
    if st.button("➕ Create New Quotation"):
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False
        st.session_state.edit_customer = None
        st.session_state.edit_status = "Draft"
        st.rerun()

    # Load Edit Data
    if st.session_state.edit_id and not st.session_state.edit_loaded:
        match = df[df["id"] == st.session_state.edit_id]
        if not match.empty:
            row = match.iloc[0]
            try: st.session_state.quote_items = json.loads(row["items"])
            except: st.session_state.quote_items = []
            st.session_state.edit_customer = row["customer_name"]
            st.session_state.edit_status = row["status"]
        st.session_state.edit_loaded = True

    # Mode Header
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")

    # Inputs
    default_cust = next((k for k, v in customer_map.items() if v == st.session_state.edit_customer), customer_options[0] if customer_options else None)
    customer_id = st.selectbox("Customer", customer_options, index=customer_options.index(default_cust) if default_cust in customer_options else 0, format_func=lambda x: customer_map[x], key="c_sel")
    status = st.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"], index=["Draft", "Sent", "Approved", "Rejected"].index(st.session_state.edit_status) if st.session_state.edit_status in ["Draft", "Sent", "Approved", "Rejected"] else 0, key="s_sel")

    st.markdown("### Items")
    item_in = st.text_input("Item", key="item_input")
    qty_in = st.number_input("Qty", value=1.0, key="qty_input")
    price_in = st.number_input("Price", value=0.0, key="price_input")

    if st.button("➕ Add Item"):
        st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": price_in})
        st.rerun()

    subtotal = 0
    updated_items = []
    for i, it in enumerate(st.session_state.quote_items):
        cols = st.columns([3, 2, 2, 1])
        n_item = cols[0].text_input("Item", it["item"], key=f"it_{i}")
        n_qty = cols[1].number_input("Qty", value=float(it["qty"]), key=f"qt_{i}")
        n_prc = cols[2].number_input("Price", value=float(it["price"]), key=f"pr_{i}")
        subtotal += n_qty * n_prc
        if cols[3].button("❌", key=f"rm_{i}"): continue
        updated_items.append({"item": n_item, "qty": n_qty, "price": n_prc})
    st.session_state.quote_items = updated_items

    # Save
    discount = st.number_input("Discount %", value=0.0, key="discount")
    tax = st.number_input("Tax %", value=0.0, key="tax")
    total = (subtotal * (1 - discount/100)) * (1 + tax/100)
    st.success(f"Subtotal: {subtotal:.2f} | Total: {total:.2f}")

    if st.button("💾 Save Quotation"):
        if not st.session_state.quote_items:
            st.error("Cannot save empty quotation!")
        else:
            cust_name = customer_map[customer_id]
            if st.session_state.edit_id:
                update_quotation(st.session_state.edit_id, cust_name, st.session_state.quote_items, subtotal, discount, tax, total, status, "V-EDIT")
            else:
                add_quotation(cust_name, st.session_state.quote_items, subtotal, discount, tax, total, status, str(date.today()), "V1")
            
            # Reset state
            st.session_state.update({"quote_items": [], "edit_id": None, "edit_loaded": False})
            st.rerun()

    # List View (Compact)
    st.markdown("---")
    st.subheader("All Quotations")
    df = get_quotations()
    if not df.empty:
        header = st.columns([3, 1, 1, 1])
        header[0].write("**Customer**"); header[1].write("**Status**"); header[2].write("**Total**"); header[3].write("**Actions**")
        for _, row in df.iterrows():
            cols = st.columns([3, 1, 1, 1])
            cols[0].write(row['customer_name'])
            cols[1].write(row['status'])
            cols[2].write(f"{row['total']:.2f}")
            btns = cols[3].columns(3)
            if btns[0].button("✏️", key=f"e_{row['id']}"):
                st.session_state.edit_id = row['id']; st.session_state.edit_loaded = False; st.rerun()
            if btns[1].button("🗑️", key=f"d_{row['id']}"):
                delete_quotation(row['id']); st.rerun()
            items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            btns[2].download_button("📄", data=generate_quotation_pdf({**row.to_dict(), "items": items}), file_name=f"q_{row['id']}.pdf", key=f"p_{row['id']}")
    else:
        st.info("No quotations found.")
