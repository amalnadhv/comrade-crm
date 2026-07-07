import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

# Import your database and utility functions
from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf

DB_NAME = "crm.db"

# --- Database Functions ---
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

# --- Page Logic ---
def quotations_page():
    st.title("💼 Quotations")

    # 1. Initialize Session State
    defaults = {
        "quote_items": [], "edit_id": None, "edit_loaded": False,
        "edit_customer": None, "edit_status": "Draft"
    }
    for key, value in defaults.items():
        if key not in st.session_state: st.session_state[key] = value

    # 2. Data Loading
    customers = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers.itertuples()}
    
    # 3. Create New Button (Resets everything)
    if st.button("➕ Create New Quotation"):
        for key in defaults: st.session_state[key] = defaults[key]
        st.rerun()

    # 4. Form Logic (Populates if editing)
    if st.session_state.edit_id and not st.session_state.edit_loaded:
        df = get_quotations()
        match = df[df["id"] == st.session_state.edit_id]
        if not match.empty:
            row = match.iloc[0]
            st.session_state.quote_items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            st.session_state.edit_status = row["status"]
        st.session_state.edit_loaded = True

    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")
    
    # [Insert your input fields here: Selectbox, Item Inputs, Totals logic...]

    if st.button("💾 Save Quotation"):
        # Logic to call add_quotation or update_quotation
        st.session_state.edit_id = None
        st.rerun()

    # 5. All Quotations List (Compact Row-Based View)
    st.markdown("---")
    st.subheader("All Quotations")
    
    df = get_quotations()
    if not df.empty:
        # Table Headers
        h1, h2, h3, h4 = st.columns([3, 1, 1, 1])
        h1.write("**Customer**"); h2.write("**Status**"); h3.write("**Total**"); h4.write("**Actions**")
        
        for _, row in df.iterrows():
            cols = st.columns([3, 1, 1, 1])
            cols[0].write(row['customer_name'])
            cols[1].write(row['status'])
            cols[2].write(f"{row['total']:.2f}")
            
            # Action cluster
            btn_col = cols[3].columns(3)
            
            # Edit Trigger
            if btn_col[0].button("✏️", key=f"e_{row['id']}"):
                st.session_state.edit_id = row["id"]
                st.session_state.edit_loaded = False
                st.rerun()
                
            # Delete Trigger
            if btn_col[1].button("🗑️", key=f"d_{row['id']}"):
                delete_quotation(row["id"])
                st.rerun()
                
            # PDF Trigger
            items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            safe_row = row.to_dict(); safe_row["items"] = items
            btn_col[2].download_button(
                "📄", data=generate_quotation_pdf(safe_row), 
                file_name=f"q_{row['id']}.pdf", key=f"p_{row['id']}"
            )
    else:
        st.info("No quotations found.")
