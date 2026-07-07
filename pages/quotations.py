import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

# --- Imports (Ensure these files exist in your project) ---
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

# ================= PAGE LOGIC =================
def quotations_page():
    st.title("💼 Quotations")

    # --- Session State Initialization ---
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False
    if "edit_customer" not in st.session_state: st.session_state.edit_customer = None
    if "edit_status" not in st.session_state: st.session_state.edit_status = "Draft"

    # --- Data Loading ---
    customers_df = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers_df.itertuples()}
    customer_options = list(customer_map.keys())

    # --- Create / Edit Buttons ---
    if st.button("➕ Create New Quotation"):
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False
        st.rerun()

    # --- Edit Mode Data Loader ---
    if st.session_state.edit_id and not st.session_state.edit_loaded:
        df = get_quotations()
        match = df[df["id"] == st.session_state.edit_id]
        if not match.empty:
            row = match.iloc[0]
            st.session_state.quote_items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            st.session_state.edit_customer = row["customer_name"]
            st.session_state.edit_status = row["status"]
        st.session_state.edit_loaded = True

    # --- Input Form ---
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")
    
    col1, col2 = st.columns(2)
    customer_id = col1.selectbox("Customer", customer_options, format_func=lambda x: customer_map[x])
    status = col2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"], index=["Draft", "Sent", "Approved", "Rejected"].index(st.session_state.edit_status))

    # Item Input UI
    item_in = st.text_input("Item Name")
    col_q, col_p, col_btn = st.columns(3)
    qty_in = col_q.number_input("Qty", value=1.0)
    prc_in = col_p.number_input("Price", value=0.0)
    if col_btn.button("➕ Add Item"):
        st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": prc_in})
        st.rerun()

    # Save Logic
    if st.button("💾 Save Quotation"):
        subtotal = sum(i['qty'] * i['price'] for i in st.session_state.quote_items)
        if st.session_state.edit_id:
            update_quotation(st.session_state.edit_id, customer_map[customer_id], st.session_state.quote_items, subtotal, 0, 0, subtotal, status, "V-EDIT")
        else:
            add_quotation(customer_map[customer_id], st.session_state.quote_items, subtotal, 0, 0, subtotal, status, str(date.today()), "V1")
        st.session_state.edit_id = None
        st.rerun()

    # --- COMPACT LIST VIEW ---
    st.markdown("---")
    st.subheader("All Quotations")
    df = get_quotations()
    
    if not df.empty:
        h = st.columns([3, 1, 1, 1])
        h[0].write("**Customer**"); h[1].write("**Status**"); h[2].write("**Total**"); h[3].write("**Actions**")
        
        for _, row in df.iterrows():
            cols = st.columns([3, 1, 1, 1])
            cols[0].write(row['customer_name'])
            cols[1].write(row['status'])
            cols[2].write(f"{row['total']:.2f}")
            
            # Action cluster
            btn = cols[3].columns(3)
            if btn[0].button("✏️", key=f"e_{row['id']}"):
                st.session_state.edit_id = row["id"]
                st.session_state.edit_loaded = False
                st.rerun()
            if btn[1].button("🗑️", key=f"d_{row['id']}"):
                delete_quotation(row["id"])
                st.rerun()
            
            # PDF Logic
            items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            safe_row = row.to_dict(); safe_row["items"] = items
            btn[2].download_button("📄", data=generate_quotation_pdf(safe_row), file_name=f"q_{row['id']}.pdf", key=f"p_{row['id']}")
    else:
        st.info("No records found.")
