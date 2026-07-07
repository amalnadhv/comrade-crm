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
    st.set_page_config(layout="wide")
    st.title("💼 Quotation Management")

    # --- Session Init ---
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None

    def reset_form():
        st.session_state.edit_id = None
        st.session_state.quote_items = []

    # --- Data ---
    customers_df = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers_df.itertuples()}
    
    # --- UI: Create Button ---
    if st.button("➕ Create New Quotation", type="primary"):
        reset_form()
        st.rerun()

    # --- Form: Edit/Create ---
    # We expand the editor if edit_id is set
    with st.expander("📝 Quotation Editor", expanded=(st.session_state.edit_id is not None)):
        
        # Load Existing Data if Editing
        if st.session_state.edit_id and not st.session_state.quote_items:
            df = get_quotations()
            match = df[df["id"] == st.session_state.edit_id]
            if not match.empty:
                st.session_state.quote_items = json.loads(match.iloc[0]["items"])

        # Form Inputs
        col1, col2 = st.columns(2)
        customer_id = col1.selectbox("Customer", list(customer_map.keys()), format_func=lambda x: customer_map[x])
        status = col2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

        st.markdown("### Items")
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        item_in = c1.text_input("Item Name")
        qty_in = c2.number_input("Qty", value=1.0)
        prc_in = c3.number_input("Price", value=0.0)
        
        if c4.button("➕ Add Item"):
            st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": prc_in})
            st.rerun()

        # Display Items List (Non-Editable for simple management, or keep your input logic here)
        subtotal = 0
        for i, it in enumerate(st.session_state.quote_items):
            subtotal += (it['qty'] * it['price'])
            st.write(f"**{it['item']}** | Qty: {it['qty']} | Price: {it['price']}")

        # Save/Cancel Buttons
        st.markdown("---")
        sc1, sc2 = st.columns([1, 10])
        
        if sc1.button("💾 Save Quotation"):
            if not st.session_state.quote_items:
                st.error("Please add at least one item!")
            else:
                cust_name = customer_map[customer_id]
                total = subtotal # Add tax/discount logic here if needed
                
                if st.session_state.edit_id:
                    update_quotation(st.session_state.edit_id, cust_name, st.session_state.quote_items, subtotal, 0, 0, subtotal, status, "V-EDIT")
                else:
                    add_quotation(cust_name, st.session_state.quote_items, subtotal, 0, 0, subtotal, status, str(date.today()), "V1")
                
                st.toast("✅ Quotation saved successfully!")
                reset_form()
                st.rerun()

        if sc2.button("❌ Cancel"):
            reset_form()
            st.rerun()

    # --- List Area ---
    st.markdown("## 📋 Quotations List")
    df = get_quotations()
    
    if not df.empty:
        header = st.columns([3, 1, 1, 2])
        header[0].write("**Customer**"); header[1].write("**Status**"); header[2].write("**Total**"); header[3].write("**Actions**")
        
        for _, row in df.iterrows():
            cols = st.columns([3, 1, 1, 2])
            cols[0].write(row['customer_name'])
            cols[1].write(row['status'])
            cols[2].write(f"**${row['total']:.2f}**")
            
            # Action cluster
            btn_col = cols[3].columns(3)
            
            # Edit: Sets state, triggers rerun to open expander
            if btn_col[0].button("✏️", key=f"e_{row['id']}"):
                st.session_state.edit_id = row['id']
                st.session_state.quote_items = [] # Clear to force reload
                st.rerun()
                
            # Delete
            if btn_col[1].button("🗑️", key=f"d_{row['id']}"):
                delete_quotation(row['id'])
                st.rerun()

            # PDF
            items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            safe_row = row.to_dict(); safe_row["items"] = items
            btn_col[2].download_button("📄", data=generate_quotation_pdf(safe_row), file_name=f"q_{row['id']}.pdf", key=f"p_{row['id']}")
    else:
        st.info("No records found.")
