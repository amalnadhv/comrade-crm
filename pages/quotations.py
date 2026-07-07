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
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False
    
    # Reset Helper
    def reset_form():
        st.session_state.edit_id = None
        st.session_state.edit_loaded = False
        st.session_state.quote_items = []

    # --- Data ---
    df = get_quotations()
    customers_df = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers_df.itertuples()}
    customer_options = list(customer_map.keys())

    # --- Form Section (Using Expander) ---
    with st.expander("📝 Add / Edit Quotation", expanded=(st.session_state.edit_id is not None)):
        
        # Load Edit Data
        if st.session_state.edit_id and not st.session_state.edit_loaded:
            match = df[df["id"] == st.session_state.edit_id]
            if not match.empty:
                row = match.iloc[0]
                try: st.session_state.quote_items = json.loads(row["items"])
                except: st.session_state.quote_items = []
                # Use a dummy variable or specific logic here if you need to load status/customer
            st.session_state.edit_loaded = True

        c1, c2 = st.columns(2)
        customer_id = c1.selectbox("Customer", customer_options, format_func=lambda x: customer_map[x])
        status = c2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

        # Item Entry
        st.markdown("### Items")
        i_col1, i_col2, i_col3, i_col4 = st.columns([3, 1, 1, 1])
        item_input = i_col1.text_input("Item Name")
        qty_input = i_col2.number_input("Qty", value=1.0)
        price_input = i_col3.number_input("Price", value=0.0)
        
        if i_col4.button("➕ Add"):
            st.session_state.quote_items.append({"item": item_input, "qty": qty_input, "price": price_input})
            st.rerun()

        # Display Added Items
        subtotal = 0
        updated_items = []
        for i, it in enumerate(st.session_state.quote_items):
            cols = st.columns([3, 1, 1, 1])
            n_item = cols[0].text(it["item"])
            n_qty = cols[1].text(f"{it['qty']}")
            n_prc = cols[2].text(f"{it['price']}")
            subtotal += float(it['qty']) * float(it['price'])
            if cols[3].button("❌", key=f"rm_{i}"):
                st.session_state.quote_items.pop(i)
                st.rerun()
            updated_items.append(it)

        st.markdown("---")
        # Totals
        discount = st.number_input("Discount %", value=0.0)
        tax = st.number_input("Tax %", value=0.0)
        total = (subtotal - (subtotal * discount / 100)) * (1 + tax / 100)
        
        st.metric("Total", f"{total:.2f}")

        # Save/Cancel Buttons
        col_s, col_c = st.columns([1, 10])
        if col_s.button("💾 Save Quotation"):
            customer_name = customer_map[customer_id]
            if st.session_state.edit_id:
                update_quotation(st.session_state.edit_id, customer_name, st.session_state.quote_items, subtotal, discount, tax, total, status, "V-EDIT")
                st.success("Updated successfully!")
            else:
                add_quotation(customer_name, st.session_state.quote_items, subtotal, discount, tax, total, status, str(date.today()), "V1")
                st.success("Saved successfully!")
            
            reset_form()
            st.rerun()
            
        if col_c.button("❌ Cancel"):
            reset_form()
            st.rerun()

    # --- List Area ---
    st.markdown("## 📋 Existing Quotations")
    if not df.empty:
        # Header
        h = st.columns([3, 1, 1, 2])
        h[0].write("**Customer**"); h[1].write("**Status**"); h[2].write("**Total**"); h[3].write("**Actions**")
        
        for _, row in df.iterrows():
            cols = st.columns([3, 1, 1, 2])
            cols[0].write(row['customer_name'])
            cols[1].write(row['status'])
            cols[2].write(f"{row['total']:.2f}")
            
            # Action cluster
            btn_col = cols[3].columns(3)
            
            if btn_col[0].button("✏️", key=f"e_{row['id']}"):
                st.session_state.edit_id = row["id"]
                st.session_state.edit_loaded = False
                st.rerun()
                
            if btn_col[1].button("🗑️", key=f"d_{row['id']}"):
                delete_quotation(row["id"])
                st.rerun()

            # PDF
            items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            safe_row = row.to_dict(); safe_row["items"] = items
            btn_col[2].download_button("📄", data=generate_quotation_pdf(safe_row), file_name=f"q_{row['id']}.pdf", key=f"p_{row['id']}")
    else:
        st.info("No quotations found.")
