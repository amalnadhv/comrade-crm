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

    # --- Session State Initialization ---
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False

    # --- Reset Function ---
    def reset_form():
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False

    # --- Create New Button ---
    if st.button("➕ Create New Quotation"):
        reset_form()
        st.rerun()

    # --- Data Retrieval ---
    customers_df = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers_df.itertuples()}
    
    # --- Edit Mode Loading ---
    if st.session_state.edit_id and not st.session_state.edit_loaded:
        df = get_quotations()
        match = df[df["id"] == st.session_state.edit_id]
        if not match.empty:
            row = match.iloc[0]
            st.session_state.quote_items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
        st.session_state.edit_loaded = True

    st.markdown("---")
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")

    # --- Inputs ---
    col1, col2 = st.columns(2)
    customer_id = col1.selectbox("Customer", list(customer_map.keys()), format_func=lambda x: customer_map[x])
    status = col2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])
    
    # --- Add Items ---
    st.markdown("### Add Items")
    i1, i2, i3, i4 = st.columns([2, 1, 1, 1])
    item_in = i1.text_input("Item Name", key="i_name")
    qty_in = i2.number_input("Qty", value=1.0, key="i_qty")
    prc_in = i3.number_input("Price", value=0.0, key="i_prc")
    
    if i4.button("➕ Add Item"):
        st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": prc_in})
        st.rerun()

    # --- Display Items ---
    subtotal = 0
    for i, it in enumerate(st.session_state.quote_items):
        cols = st.columns([3, 1, 1, 1])
        cols[0].write(it['item'])
        cols[1].write(f"Qty: {it['qty']}")
        cols[2].write(f"Price: {it['price']}")
        subtotal += (it['qty'] * it['price'])
        if cols[3].button("🗑️", key=f"del_{i}"):
            st.session_state.quote_items.pop(i)
            st.rerun()

    # --- Totals ---
    st.write(f"**Subtotal: {subtotal:.2f}**")
    discount = st.number_input("Discount %", value=0.0)
    tax = st.number_input("Tax %", value=0.0)
    total = (subtotal - (subtotal * discount / 100)) * (1 + tax / 100)
    st.write(f"### Total: {total:.2f}")

    # --- Action Buttons ---
    sc1, sc2 = st.columns(2)
    if sc1.button("💾 Save Quotation"):
        if not st.session_state.quote_items:
            st.error("Please add at least one item.")
        else:
            cust_name = customer_map[customer_id]
            if st.session_state.edit_id:
                update_quotation(st.session_state.edit_id, cust_name, st.session_state.quote_items, subtotal, discount, tax, total, status, "V-EDIT")
                st.success("Updated successfully!")
            else:
                add_quotation(cust_name, st.session_state.quote_items, subtotal, discount, tax, total, status, str(date.today()), "V1")
                st.success("Saved successfully!")
            
            # Reset and rerun to clear the screen
            reset_form()
            st.rerun()

    if sc2.button("❌ Cancel"):
        reset_form()
        st.rerun()

    # --- List Display ---
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
            
        items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
        pdf_data = generate_quotation_pdf({**row.to_dict(), "items": items})
        c3.download_button("📄 PDF", data=pdf_data, file_name=f"quote_{row['id']}.pdf", key=f"pdf_{row['id']}")
