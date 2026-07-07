import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

# --- Database/Utils Imports ---
from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf

DB_NAME = "crm.db"

# ================= PAGE LOGIC =================
def quotations_page():
    st.set_page_config(layout="wide")
    st.title("💼 Quotation Management")
    
    # 1. State Management
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_editor" not in st.session_state: st.session_state.show_editor = False

    def reset_form():
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.show_editor = False

    # 2. Data Loading
    customers = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers.itertuples()}

    # 3. UI Controls
    if st.button("➕ Create New Quotation", type="primary"):
        reset_form()
        st.session_state.show_editor = True
        st.rerun()

    # 4. Input Editor
    with st.expander("📝 Quotation Editor", expanded=st.session_state.show_editor):
        # Trigger data loading for edit
        if st.session_state.edit_id and not st.session_state.quote_items:
            df = get_quotations()
            match = df[df["id"] == st.session_state.edit_id]
            if not match.empty:
                st.session_state.quote_items = json.loads(match.iloc[0]["items"])
        
        # Form Fields
        cust_id = st.selectbox("Customer", list(customer_map.keys()), format_func=lambda x: customer_map[x])
        
        # ... (Include your Item Input and Loop logic here) ...

        # Buttons
        col_s, col_c = st.columns([1, 10])
        if col_s.button("💾 Save"):
            # (Insert your Save/Update logic here)
            reset_form()
            st.rerun()
        if col_c.button("❌ Cancel"):
            reset_form()
            st.rerun()

    # 5. List View (Fixed for Edit/Delete Buttons)
    st.markdown("## 📋 Quotations List")
    df = get_quotations()
    
    if not df.empty:
        h = st.columns([3, 1, 1, 2])
        h[0].write("**Customer**"); h[1].write("**Status**"); h[2].write("**Total**"); h[3].write("**Actions**")
        
        for idx, row in df.iterrows():
            cols = st.columns([3, 1, 1, 2])
            cols[0].write(row['customer_name'])
            cols[1].write(row['status'])
            cols[2].write(f"**${row['total']:.2f}**")
            
            # Action Buttons
            act = cols[3].columns(3)
            # Use a unique key based on row ID
            if act[0].button("✏️", key=f"edit_btn_{row['id']}"):
                st.session_state.edit_id = row['id']
                st.session_state.quote_items = [] # Force load
                st.session_state.show_editor = True
                st.rerun()
            
            if act[1].button("🗑️", key=f"del_btn_{row['id']}"):
                delete_quotation(row['id'])
                st.rerun()
    else:
        st.info("No records found.")
