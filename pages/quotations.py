import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

# Imports
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
    # Page setup
    st.set_page_config(layout="wide")
    st.title("💼 Quotation Management")
    
    # 1. State Management
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False

    # 2. Reset Function
    def reset_form():
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False

    # --- UI: Create New ---
    if st.button("➕ Create New Quotation", type="primary"):
        reset_form()
        st.rerun()

    # --- UI: Input Form (Expander) ---
    with st.expander("📝 Quotation Editor", expanded=(st.session_state.edit_id is not None)):
        # Load logic
        if st.session_state.edit_id and not st.session_state.edit_loaded:
            df = get_quotations()
            match = df[df["id"] == st.session_state.edit_id]
            if not match.empty:
                st.session_state.quote_items = json.loads(match.iloc[0]["items"])
            st.session_state.edit_loaded = True

        col1, col2 = st.columns(2)
        customer = col1.selectbox("Customer", ["Customer A", "Customer B"]) # Replace with your dynamic list
        status = col2.selectbox("Status", ["Draft", "Sent", "Approved"])

        st.markdown("---")
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        item_in = c1.text_input("Item Name")
        qty_in = c2.number_input("Qty", value=1.0)
        prc_in = c3.number_input("Price", value=0.0)
        if c4.button("Add Item"):
            st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": prc_in})
            st.rerun()

        # Display items
        subtotal = sum(i['qty'] * i['price'] for i in st.session_state.quote_items)
        for i, it in enumerate(st.session_state.quote_items):
            st.write(f"{it['item']} | {it['qty']} x ${it['price']}")

        # Save/Cancel
        s1, s2 = st.columns([1, 8])
        if s1.button("💾 Save"):
            # (Save Logic here)
            reset_form() # Blank screen after save
            st.success("Saved!")
            st.rerun()
        if s2.button("❌ Cancel"):
            reset_form() # Clear form on cancel
            st.rerun()

    # --- UI: Attractive List View ---
    st.markdown("## 📋 Quotations List")
    df = get_quotations()
    
    if not df.empty:
        header = st.columns([3, 1, 1, 2])
        header[0].markdown("**Customer**"); header[1].markdown("**Status**"); header[2].markdown("**Total**"); header[3].markdown("**Actions**")
        
        for _, row in df.iterrows():
            cols = st.columns([3, 1, 1, 2])
            cols[0].write(row['customer_name'])
            cols[1].write(row['status'])
            cols[2].write(f"**${row['total']:.2f}**")
            
            actions = cols[3].columns(3)
            if actions[0].button("✏️", key=f"e_{row['id']}"):
                st.session_state.edit_id = row['id']
                st.session_state.edit_loaded = False
                st.rerun()
            if actions[1].button("🗑️", key=f"d_{row['id']}"):
                delete_quotation(row['id'])
                st.rerun()
            # PDF download ...
    else:
        st.info("No records found.")
