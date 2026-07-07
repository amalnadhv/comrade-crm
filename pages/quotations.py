import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf, generate_list_pdf

DB_NAME = "crm.db"

# ================= DATABASE FUNCTIONS =================
# (Unchanged)
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
    # --- Custom CSS for Themes and Colors ---
    st.markdown("""
        <style>
            /* Status Badges */
            .status-pill { padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 0.8rem; color: white; }
            .Draft { background-color: #95a5a6; }
            .Sent { background-color: #3498db; }
            .Approved { background-color: #27ae60; }
            .Rejected { background-color: #e74c3c; }
            
            /* Container styling */
            .input-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #3498db; }
            
            /* Metric Highlight */
            .total-highlight { color: #2c3e50; font-weight: bold; }
            .status-pill { padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 0.8rem; color: white; }
            
            .Draft { background-color: #7f8c8d; }     /* Neutral Grey */
            .Sent { background-color: #2563EB; }      /* Vibrant Blue */
            .Approved { background-color: #059669; }  /* Vibrant Emerald Green */
            .Rejected { background-color: #DC2626; }  /* Vibrant Red */
            
            .input-box { 
                background-color: #f8f9fa; 
                padding: 20px; 
                border-radius: 10px; 
                border-left: 5px solid #2563EB; /* Matching Vibrant Blue */
            }
        </style>
    """, unsafe_allow_html=True)

    def render_status_badge(status):
        return f'<span class="status-pill {status}">{status}</span>'

    st.title("💼 Quotations Dashboard")

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

    # --- Navigation ---
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

    # --- COLORFUL INPUT SECTION ---
    st.markdown('<div class="input-box">', unsafe_allow_html=True)
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")
    col1, col2 = st.columns(2)
    customer_id = col1.selectbox("Customer", list(customer_map.keys()), format_func=lambda x: customer_map[x])
    status = col2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])
    
    st.markdown("### 📝 Add Items")
    i1, i2, i3, i4 = st.columns([2, 1, 1, 1])
    item_in = i1.text_input("Item Name", key=f"i_name_{st.session_state.form_id}")
    qty_in = i2.number_input("Qty", value=1.0, key=f"i_qty_{st.session_state.form_id}")
    prc_in = i3.number_input("Price", value=0.0, key=f"i_prc_{st.session_state.form_id}")
    
    if i4.button("➕ Add Item"):
        st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": prc_in})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True) # Close colored box

    # --- TOTALS ---
    subtotal = sum(it['qty'] * it['price'] for it in st.session_state.quote_items)
    discount = st.number_input("Discount %", value=0.0)
    tax = st.number_input("Tax %", value=0.0)
    total = (subtotal - (subtotal * discount / 100)) * (1 + tax / 100)

    # Use a container for totals to make them pop
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.metric("Subtotal", f"{subtotal:,.2f}")
        c2.metric("Total Amount", f"{total:,.2f}")

    # --- ACTIONS ---
    sc1, sc2 = st.columns([1, 5])
    if sc1.button("💾 Save Quotation"):
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

  # --- LIST DISPLAY, SEARCH, FILTER, & EXPORT ---
    st.divider()
    st.subheader("📋 All Quotations")

    # 1. Search & Filter Inputs (Changed [2, 1, 1] to [2, 1, 1, 1] to add space for PDF button)
    col_search, col_filter, col_export, col_pdf = st.columns([2, 1, 1, 1])
    search_val = col_search.text_input("🔍 Search by Customer Name", key="search_query")
    status_val = col_filter.multiselect("Filter by Status", ["Draft", "Sent", "Approved", "Rejected"], key="status_filter")

    # 2. Get Data and Apply Filters
    df = get_quotations()
    
    if search_val:
        df = df[df['customer_name'].str.contains(search_val, case=False, na=False)]
    
    if status_val:
        df = df[df['status'].isin(status_val)]
    
    # 3. Export Buttons (CSV and PDF)
    csv_data = df.to_csv(index=False).encode('utf-8')
    col_export.download_button(
        label="📥 Export CSV",
        data=csv_data,
        file_name="filtered_quotations.csv",
        mime="text/csv",
        key="export_csv"
    )

    # Added PDF Button
    col_pdf.download_button(
        label="📄 Export PDF",
        data=generate_list_pdf(df), 
        file_name="filtered_report.pdf",
        mime="application/pdf",
        key="export_pdf"
    )

    # 4. Render Header and Filtered Rows (Rest remains exactly as you had it)
    head_c1, head_c2, head_c3, head_c4 = st.columns([3, 2, 2, 3])
    head_c1.markdown("**Customer**"); head_c2.markdown("**Status**"); head_c3.markdown("**Total**"); head_c4.markdown("**Actions**")
    
    if df.empty:
        st.info("No quotations found matching your search.")
    else:
        for _, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
            c1.write(row.get('customer_name', 'N/A'))
            c2.markdown(render_status_badge(row.get('status', 'Draft')), unsafe_allow_html=True)
            c3.write(f"{row.get('total', 0):,.2f}")
            
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
                s3.download_button(
                    label="📄", 
                    data=generate_quotation_pdf({**row.to_dict(), "items": items}), 
                    file_name=f"q_{row['id']}.pdf", 
                    key=f"pdf_{row['id']}"
                )
