import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

# Import your database and utility functions
from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf

DB_NAME = "crm.db"

# --- Keep your existing functions here ---
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

def quotations_page():
    st.title("💼 Quotations")

    # Session State Initialization
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False
    
    # --- Input Form Area ---
    # (Your existing form logic goes here...)
    
    # --- All Quotations List (The List View) ---
    st.markdown("---")
    st.subheader("All Quotations")

    df = get_quotations()
    
    if not df.empty:
        # Define the header for the list view
        header = st.columns([3, 2, 2, 2])
        header[0].write("**Customer**")
        header[1].write("**Status**")
        header[2].write("**Total**")
        header[3].write("**Actions**")
        
        # Display each record in a simple row
        for _, row in df.iterrows():
            cols = st.columns([3, 2, 2, 2])
            
            cols[0].write(row['customer_name'])
            cols[1].write(row['status'])
            cols[2].write(f"{row['total']:.2f}")
            
            # Action cluster
            btn_col = cols[3].columns(3)
            
            if btn_col[0].button("✏️", key=f"edit_{row['id']}"):
                st.session_state.edit_id = row["id"]
                st.session_state.edit_loaded = False
                st.rerun()
                
            if btn_col[1].button("🗑️", key=f"del_{row['id']}"):
                delete_quotation(row["id"])
                st.rerun()
                
            # PDF Logic
            items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            safe_row = row.to_dict()
            safe_row["items"] = items
            
            btn_col[2].download_button(
                label="📄", 
                data=generate_quotation_pdf(safe_row), 
                file_name=f"quote_{row['id']}.pdf", 
                key=f"pdf_{row['id']}"
            )
    else:
        st.info("No quotations found.")
