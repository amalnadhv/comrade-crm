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
        UPDATE quotations SET customer_name=?, items=?, subtotal=?, discount=?, tax=?, total=?, status=?, version=? 
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

    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False

    def reset_form():
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False

    if st.button("➕ Create New Quotation"):
        reset_form()
        st.rerun()

    customers_df = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers_df.itertuples()}
    
    if st.session_state.edit_id and not st.session_state.edit_loaded:
        df = get_quotations()
        match = df[df["id"] == st.session_state.edit_id]
        if not match.empty:
            row = match.iloc[0]
            st.session_state.quote_items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
        st.session_state.edit_loaded = True

    st.markdown("---")
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")

    # --- INPUT FORM ---
    with st.form("quotation_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        customer_id = col1.selectbox("Customer", list(customer_map.keys()), format_func=lambda x: customer_map[x])
        status = col2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])
        
        # We handle items logic outside of the form to keep it dynamic
        # Note: Added items are tracked in session_state, not form input
        
        submitted = st.form_submit_button("💾 Save Quotation")
        
        if submitted:
            if not st.session_state.quote_items:
                st.error("Please add at least one item.")
            else:
                cust_name = customer_map[customer_id]
                subtotal = sum(it['qty'] * it['price'] for it in st.session_state.quote_items)
                # (Add tax/discount logic here if needed, or pull from fields)
                
                if st.session_state.edit_id:
                    update_quotation(st.session_state.edit_id, cust_name, st.session_state.quote_items, subtotal, 0, 0, subtotal, status, "V-EDIT")
                    st.success("Updated successfully!")
                else:
                    add_quotation(cust_name, st.session_state.quote_items, subtotal, 0, 0, subtotal, status, str(date.today()), "V1")
                    st.success("Saved successfully!")
                
                reset_form()
                st.rerun()

    # --- Item Management (Outside Form) ---
    st.markdown("### Add Items")
    i1, i2, i3, i4 = st.columns([2, 1, 1, 1])
    item_in = i1.text_input("Item Name", key="i_name")
    qty_in = i2.number_input("Qty", value=1.0, key="i_qty")
    prc_in = i3.number_input("Price", value=0.0, key="i_prc")
    
    if i4.button("➕ Add"):
        st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": prc_in})
        st.rerun()

    # List Display
    for i, it in enumerate(st.session_state.quote_items):
        cols = st.columns([3, 1, 1, 1])
        cols[0].write(it['item'])
        cols[1].write(f"Qty: {it['qty']}")
        cols[2].write(f"Price: {it['price']}")
        if cols[3].button("🗑️", key=f"del_{i}"):
            st.session_state.quote_items.pop(i)
            st.rerun()

    # --- List View ---
    st.markdown("---")
    st.subheader("All Quotations")
    df = get_quotations()
    for _, row in df.iterrows():
        st.markdown(f"### {row.get('customer_name')} | Status: {row.get('status')} | Total: {row.get('total', 0):.2f}")
        c1, c2, c3 = st.columns(3)
        if c1.button("✏️ Edit", key=f"e_{row['id']}"):
            st.session_state.edit_id = row["id"]
            st.session_state.edit_loaded = False
            st.rerun()
        if c2.button("🗑️ Delete", key=f"d_{row['id']}"):
            delete_quotation(row["id"])
            st.rerun()
