import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf

DB_NAME = "crm.db"

# --- Database Functions ---
def update_quotation(qid, customer_name, items, subtotal, discount, tax, total, status, version):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE quotations SET customer_name=?, items=?, subtotal=?, discount=?, tax=?, total=?, status=?, version=? WHERE id=?", 
                (customer_name, json.dumps(items), subtotal, discount, tax, total, status, version, qid))
    conn.commit()
    conn.close()

def delete_quotation(qid):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM quotations WHERE id=?", (qid,))
    conn.commit()
    conn.close()

# --- Page Logic ---
def quotations_page():
    st.set_page_config(layout="wide")
    st.title("💼 Quotation Management")

    # Initialize State
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None

    # Helper: Clear everything
    def reset_screen():
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.rerun()

    # --- TOP CONTROL: Create New ---
    if st.button("➕ Create New Quotation", type="primary"):
        reset_screen() # Clears everything and reruns

    # --- EDITOR SECTION ---
    # We only show this if we are editing (edit_id is set) or Creating (we manage via logic)
    # To keep it simple: if you clicked 'Create' or 'Edit', we show the form.
    
    # Check if we are in 'Edit' mode and need to load data
    if st.session_state.edit_id is not None:
        # Load logic here once
        if not st.session_state.quote_items:
            df = get_quotations()
            match = df[df["id"] == st.session_state.edit_id]
            if not match.empty:
                st.session_state.quote_items = json.loads(match.iloc[0]["items"])
    
    st.markdown("---")
    st.subheader("📝 Edit/Create Quotation")
    
    # Customer Selection
    cust_data = get_customers()
    cust_map = {r[0]: f"{r[1]} ({r[4]})" for r in cust_data}
    c1, c2 = st.columns(2)
    sel_cust = c1.selectbox("Customer", list(cust_map.keys()), format_func=lambda x: cust_map[x])
    sel_status = c2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

    # Item Input
    st.markdown("### Items")
    i1, i2, i3, i4 = st.columns([2, 1, 1, 1])
    item = i1.text_input("Item Name")
    qty = i2.number_input("Qty", value=1.0)
    price = i3.number_input("Price", value=0.0)
    
    if i4.button("Add Item"):
        st.session_state.quote_items.append({"item": item, "qty": qty, "price": price})
        st.rerun()

    # Display Items (Read-only list to prevent duplication issues)
    subtotal = 0
    for i, it in enumerate(st.session_state.quote_items):
        col_list = st.columns([3, 1, 1, 1])
        col_list[0].write(it['item'])
        col_list[1].write(f"Qty: {it['qty']}")
        col_list[2].write(f"Price: {it['price']}")
        subtotal += (it['qty'] * it['price'])
        if col_list[3].button("🗑️", key=f"del_{i}"):
            st.session_state.quote_items.pop(i)
            st.rerun()

    st.write(f"**Subtotal: {subtotal:.2f}**")

    # Save / Cancel
    s1, s2 = st.columns(2)
    if s1.button("💾 Save"):
        if not st.session_state.quote_items:
            st.error("Add items first!")
        else:
            if st.session_state.edit_id:
                update_quotation(st.session_state.edit_id, cust_map[sel_cust], st.session_state.quote_items, subtotal, 0, 0, subtotal, sel_status, "V-EDIT")
            else:
                add_quotation(cust_map[sel_cust], st.session_state.quote_items, subtotal, 0, 0, subtotal, sel_status, str(date.today()), "V1")
            
            st.toast("Saved Successfully!")
            reset_screen()
    
    if s2.button("❌ Cancel"):
        reset_screen()

    # --- LIST VIEW ---
    st.markdown("---")
    st.subheader("All Quotations")
    df = get_quotations()
    for _, row in df.iterrows():
        cols = st.columns([3, 1, 1, 2])
        cols[0].write(row['customer_name'])
        cols[1].write(row['status'])
        cols[2].write(f"{row['total']:.2f}")
        
        # Action Buttons
        a1, a2, a3 = cols[3].columns(3)
        if a1.button("✏️", key=f"e_{row['id']}"):
            st.session_state.edit_id = row['id']
            st.session_state.quote_items = [] # Trigger reload
            st.rerun()
        if a2.button("🗑️", key=f"d_{row['id']}"):
            delete_quotation(row['id'])
            st.rerun()
