import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF
from streamlit_calendar import calendar

from database import (
    add_followup, get_followups, get_leads, get_customers,
    delete_followup, update_followup
)

# =====================================================
# UTILS & PDF GENERATOR
# =====================================================
def load_followups():
    df = get_followups()
    return df if df is not None else pd.DataFrame()

def show_message(msg):
    st.session_state["follow_msg"] = msg

def render_message():
    if st.session_state.get("follow_msg"):
        st.success(st.session_state.follow_msg)
        st.session_state.follow_msg = None

def clear_followup_form():
    keys = ["follow_type", "follow_lead", "follow_customer", "follow_title", "follow_date", "follow_status", "follow_remarks"]
    for key in keys:
        st.session_state.pop(key, None)

def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Follow-up Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Title", border=1)
    pdf.cell(40, 10, "Date", border=1)
    pdf.cell(40, 10, "Status", border=1)
    pdf.ln()
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(60, 10, str(row['title']), border=1)
        pdf.cell(40, 10, str(row['followup_date']), border=1)
        pdf.cell(40, 10, str(row['status']), border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# =====================================================
# PAGE
# =====================================================
def followups_page():
    # Session States
    if "followup_saved" not in st.session_state: st.session_state.followup_saved = True
    if "edit_followup_id" not in st.session_state: st.session_state.edit_followup_id = None

    # CSS
    st.markdown("""
    <style>
    .crm-header { background: linear-gradient(135deg, #667eea, #764ba2); padding:22px 30px; border-radius:15px; margin-bottom:15px; box-shadow: 0 4px 12px rgba(0,0,0,.15); }
    .crm-title { color:white; font-size:32px; font-weight:800; }
    .crm-subtitle { color:#f3eaff; font-size:15px; margin-top:6px; }
    .table-header { background: linear-gradient(135deg, #667eea, #764ba2); color:white; padding:8px; border-radius:8px; text-align:center; font-weight:bold; }
    .status-pending { color:#ff9800; font-weight:bold; }
    .status-done { color:#28a745; font-weight:bold; }
    .status-overdue { color:#dc3545; font-weight:bold; }
    div.stButton > button { border-radius:10px; height:36px; font-weight:bold; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="crm-header"><div class="crm-title">📅 Follow-up Management</div><div class="crm-subtitle">Track activities and pending actions efficiently</div></div>', unsafe_allow_html=True)
    render_message()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Management", "📅 Calendar", "📄 Export"])

    df = load_followups()

    with tab1:
        # --- YOUR EXISTING MANAGEMENT CODE ---
        leads = get_leads() or pd.DataFrame()
        customers = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"]) if get_customers() is not None else pd.DataFrame()

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(df))
        c2.metric("Pending", len(df[df.status=="Pending"]) if not df.empty else 0)
        c3.metric("Done", len(df[df.status=="Done"]) if not df.empty else 0)
        c4.metric("Overdue", len(df[df.status=="Overdue"]) if not df.empty else 0)

        if st.button("➕ New Follow-up", width="stretch"):
            st.session_state.followup_saved = False
        
        # [ADD YOUR FORM AND TABLE RENDERING LOGIC HERE AS PREVIOUSLY PROVIDED]
        st.write("---")
        search = st.text_input("🔍 Search Follow-ups")
        # (Include your search filtering and table loops here)

    with tab2:
        st.subheader("📅 Interactive Schedule")
        if not df.empty:
            events = [{"title": r.title, "start": r.followup_date, "backgroundColor": "#28a745" if r.status == "Done" else "#ff9800"} for r in df.itertuples()]
            calendar(events=events, options={"initialView": "dayGridMonth"})
        else:
            st.info("No schedule data found.")

    with tab3:
        st.subheader("📄 Export Reports")
        if not df.empty:
            st.download_button("⬇ Download PDF Report", data=generate_pdf(df), file_name="followups.pdf", mime="application/pdf")
        else:
            st.warning("No data to export.")
