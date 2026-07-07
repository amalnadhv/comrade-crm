import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3
from fpdf import FPDF
import io

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

# ================= REPORTING FUNCTIONS =================
def generate_report_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Quotations Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    cols = ["Customer", "Approved", "Rejected", "Total Value"]
    for col in cols: pdf.cell(45, 10, col, border=1)
    pdf.ln()
    for _, row in df.iterrows():
        pdf.cell(45, 10, str(row['customer_name']), border=1)
        pdf.cell(45, 10, str(row['Approved']), border=1)
        pdf.cell(45, 10, str(row['Rejected']), border=1)
        pdf.cell(45, 10, f"{row['total_value']:.2f}", border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

def render_reports():
    st.divider()
    st.subheader("📊 Analytics & Reports")
    df = get_quotations()
    if df.empty:
        st.info("No data available for reports yet.")
        return
    
    report_df = df.groupby('customer_name').agg(
        Approved=('status', lambda x: (x == 'Approved').sum()),
        Rejected=('status', lambda x: (x == 'Rejected').sum()),
        total_value=('total', 'sum')
    ).reset_index()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Quotations", len(df))
    col2.metric("Success", f"{report_df['Approved'].sum()}")
    col3.metric("Failed", f"{report_df['Rejected'].sum()}")

    st.dataframe(report_df, use_container_width=True)
    c1, c2 = st.columns(2)
    c1.download_button("📥 Download CSV", data=report_df.to_csv(index=False).encode('utf-8'), file_name='report.csv', mime='text/csv')
    c2.download_button("📥 Download PDF", data=generate_report_pdf(report_df), file_name='report.pdf', mime='application/pdf')

# ================= PAGE =================
def quotations_page():
    st.markdown("""
        <style>
            .status-pill { padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 0.8rem; color: white; }
            .Draft { background-color: #95a5a6; } .Sent { background-color: #3498db; }
            .Approved { background-color: #27ae60; } .Rejected { background-color: #e74c3c; }
            .input-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #3498db; }
        </style>
    """, unsafe_allow_html=True)

    def render_status_badge(status): return f'<span class="status-pill {status}">{status}</span>'

    if "quote_items" not in st.session_state: st.session_state.quote_items = []
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "edit_loaded" not in st.session_state: st.session_state.edit_loaded = False
    if "form_id" not in st.session_state: st.session_state.form_id = 0

    def reset_form():
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False
        st.session_state.form_id += 1

    st.title("💼 Quotations Dashboard")
    if st.button("➕ Create New Quotation"):
        reset_form(); st.rerun()

    # (Add your existing Customer Loading logic here...)
    customers_df = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers_df.itertuples()}

    # --- INPUT SECTION ---
    st.markdown('<div class="input-box">', unsafe_allow_html=True)
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")
    col1, col2 = st.columns(2)
    customer_id = col1.selectbox("Customer", list(customer_map.keys()), format_func=lambda x: customer_map[x])
    status = col2.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])
    
    i1, i2, i3, i4 = st.columns([2, 1, 1, 1])
    item_in = i1.text_input("Item", key=f"i_name_{st.session_state.form_id}")
    qty_in = i2.number_input("Qty", value=1.0, key=f"i_qty_{st.session_state.form_id}")
    prc_in = i3.number_input("Price", value=0.0, key=f"i_prc_{st.session_state.form_id}")
    if i4.button("➕ Add Item"):
        st.session_state.quote_items.append({"item": item_in, "qty": qty_in, "price": prc_in})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SEARCH & LIST ---
    st.divider()
    st.subheader("📋 All Quotations")
    col_s, col_f = st.columns([2, 1])
    search = col_s.text_input("🔍 Search")
    status_filter = col_f.multiselect("Filter Status", ["Draft", "Sent", "Approved", "Rejected"])
    
    df = get_quotations()
    if search: df = df[df['customer_name'].str.contains(search, case=False, na=False)]
    if status_filter: df = df[df['status'].isin(status_filter)]

    for _, row in df.iterrows():
        c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
        c1.write(row.get('customer_name'))
        c2.markdown(render_status_badge(row.get('status')), unsafe_allow_html=True)
        c3.write(f"{row.get('total', 0):,.2f}")
        with c4:
            if st.button("✏️", key=f"e_{row['id']}"): 
                st.session_state.edit_id = row["id"]; st.rerun()

    # --- CALL THE REPORTS FUNCTION ---
    render_reports()
