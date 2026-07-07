import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf

DB_NAME = "crm.db"

# ================= DATABASE FUNCTIONS =================
# (Kept identical to your working version)
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
    # --- CSS for Colored Status Badges ---
    st.markdown("""
        <style>
            .status-pill {
                padding: 4px 10px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 0.8rem;
                color: white;
            }
            .Draft { background-color: #7f8c8d; }
            .Sent { background-color: #3498db; }
            .Approved { background-color: #27ae60; }
            .Rejected { background-color: #c0392b; }
        </style>
    """, unsafe_allow_html=True)

    def render_status_badge(status):
        return f'<span class="status-pill {status}">{status}</span>'

    st.title("💼 Quotations")

    # --- Session State ---
    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False
    if "form_id" not in st.session_state: st.session_state.form_id = 0

    def reset_form():
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False
        st.session_state.form_id += 1

    # --- Navigation & Data ---
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

    # --- INPUT CONTAINER ---
    with st.container(border=True):
        st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")
        col1, col2 = st.columns(2)
        customer_id = col1.selectbox("Customer", list(customer_map.keys()), format_func=lambda x: customer_map[x])
        status = col2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])
        
        st.markdown("### Add Items")
        i1, i2, i3, i4 = st.columns([2, 1, 1, 1])
        item_in = i1.text_input("Item Name", key=f"i_name_{st.session_state.form_id}")
        qty_in = i2.number_input("Qty", value=1.0, key=f"i_qty_{st.session_state.form_id}")
        prc_in = i3.number_input("Price", value=0.0, key=f"i_prc_{st.session_state.form_id}")
        
        if i4.button("➕ Add Item"):
            st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": prc_in})
            st.rerun()

    # --- ITEMS TABLE ---
    if st.session_state.quote_items:
        st.markdown("#### Current Items")
        for i, it in enumerate(st.session_state.quote_items):
            cols = st.columns([3, 1, 1, 1])
            cols[0].write(it['item'])
            cols[1].write(f"Qty: {it['qty']}")
            cols[2].write(f"Price: {it['price']}")
            if cols[3].button("🗑️", key=f"del_{i}"):
                st.session_state.quote_items.pop(i)
                st.rerun()

    # --- TOTALS METRICS ---
    subtotal = sum(it['qty'] * it['price'] for it in st.session_state.quote_items)
    discount = st.number_input("Discount %", value=0.0)
    tax = st.number_input("Tax %", value=0.0)
    total = (subtotal - (subtotal * discount / 100)) * (1 + tax / 100)

    c1, c2 = st.columns(2)
    c1.metric("Subtotal", f"{subtotal:.2f}")
    c2.metric("Total Amount", f"{total:.2f}")

    # --- ACTIONS ---
    sc1, sc2 = st.columns([1, 5])
    if sc1.button("💾 Save"):
        if not st.session_state.quote_items:
            st.error("Please add at least one item.")
        else:
            cust_name = customer_map[customer_id]
            if st.session_state.edit_id:
                update_quotation(st.session_state.edit_id, cust_name, st.session_state.quote_items, subtotal, discount, tax, total, status, "V-EDIT")
            else:
                add_quotation(cust_name, st.session_state.quote_items, subtotal, discount, tax, total, status, str(date.today()), "V1")
            reset_form()
            st.rerun()
    if sc2.button("❌ Cancel"):
        reset_form()
        st.rerun()

    # --- LIST DISPLAY ---
    st.divider()
    st.subheader("📋 All Quotations")
    head_c1, head_c2, head_c3, head_c4 = st.columns([3, 2, 2, 3])
    head_c1.markdown("**Customer**"); head_c2.markdown("**Status**"); head_c3.markdown("**Total**"); head_c4.markdown("**Actions**")
    
    df = get_quotations()
    for _, row in df.iterrows():
        c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
        c1.write(row.get('customer_name', 'N/A'))
        
        # Apply the Colored Badge here
        c2.markdown(render_status_badge(row.get('status', 'Draft')), unsafe_allow_html=True)
        
        c3.write(f"{row.get('total', 0):.2f}")
        
        with c4:
            s1, s2, s3 = st.columns(3)
            if s1.button("✏️", key=f"e_{row['id']}"):
                st.session_state.edit_id = row["id"]
                st.session_state.edit_loaded = False
                st.rerun()
            if s2.button("🗑️", key=f"d_{row['id']}"):
                delete_quotation(row["id"])
                st.rerun()
            items = json.loads(row["items"]) if isinstance(row["items"], str) else row["items"]
            s3.download_button("📄", data=generate_quotation_pdf({**row.to_dict(), "items": items}), file_name=f"q_{row['id']}.pdf", key=f"pdf_{row['id']}")
