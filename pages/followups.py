import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF
from streamlit_calendar import calendar

from database import (
    add_followup,
    get_followups,
    get_leads,
    get_customers,
    delete_followup,
    update_followup
)

# =====================================================
# LOAD DATA
# =====================================================
def load_followups():
    df = get_followups()
    if df is None:
        return pd.DataFrame()
    return df

# =====================================================
# MESSAGE SYSTEM
# =====================================================
def show_message(msg):
    st.session_state["follow_msg"] = msg

def render_message():
    if st.session_state.get("follow_msg"):
        st.success(st.session_state.follow_msg)
        st.session_state.follow_msg = None

# =====================================================
# CLEAR FORM
# =====================================================
def clear_followup_form():
    keys = [
        "follow_type",
        "follow_lead",
        "follow_customer",
        "follow_title",
        "follow_date",
        "follow_status",
        "follow_remarks"
    ]
    for key in keys:
        st.session_state.pop(key, None)

# =====================================================
# PDF GENERATOR
# =====================================================
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt="Follow-up Report", ln=True, align='C')
    pdf.ln(10)
    
    # Secure structural column widths (Total width exactly 190mm for A4)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(90, 10, "Title", border=1)
    pdf.cell(50, 10, "Date", border=1)
    pdf.cell(50, 10, "Status", border=1)
    pdf.ln()
    
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(90, 10, str(row.get('title', '-')), border=1)
        pdf.cell(50, 10, str(row.get('followup_date', '-')), border=1)
        pdf.cell(50, 10, str(row.get('status', '-')), border=1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# =====================================================
# MAIN PAGE IMPLEMENTATION
# =====================================================
def followups_page():
    role = st.session_state.user["role"]

    # =================================================
    # SESSION CONTROL
    # =================================================
    if "followup_saved" not in st.session_state:
        st.session_state.followup_saved = True

    if "edit_followup_id" not in st.session_state:
        st.session_state.edit_followup_id = None

    # =================================================
    # CSS STYLING
    # =================================================
    st.markdown(
    """
    <style>
    .crm-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding:22px 30px;
        border-radius:15px;
        margin-bottom:15px;
        box-shadow: 0 4px 12px rgba(0,0,0,.15);
    }

    .crm-title {
        color:white;
        font-size:32px;
        font-weight:800;
    }

    .crm-subtitle {
        color:#f3eaff;
        font-size:15px;
        margin-top:6px;
    }

    .table-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color:white;
        padding:8px;
        border-radius:8px;
        text-align:center;
        font-weight:bold;
    }

    .status-pending {
        color:#ff9800;
        font-weight:bold;
    }

    .status-done {
        color:#28a745;
        font-weight:bold;
    }

    .status-overdue {
        color:#dc3545;
        font-weight:bold;
    }

    div.stButton > button {
        border-radius:10px;
        height:36px;
        font-weight:bold;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

    # =================================================
    # HEADER
    # =================================================
    st.markdown(
    """
    <div class="crm-header">
        <div class="crm-title">
            📅 Follow-up Management
        </div>
        <div class="crm-subtitle">
            Track customer activities, reminders and pending actions efficiently
        </div>
    </div>
    """,
    unsafe_allow_html=True
    )

    render_message()

    # Safe Data Extraction (Resolves the Ambiguous DataFrame Truth Value crash)
    df = load_followups()

    leads = get_leads()
    if leads is None:
        leads = pd.DataFrame()

    customers_raw = get_customers()
    if customers_raw is None:
        customers = pd.DataFrame()
    else:
        customers = pd.DataFrame(
            customers_raw,
            columns=["id", "name", "phone", "email", "company", "status"]
        )

    # =================================================
    # NAVIGATION TABS
    # =================================================
    tab1, tab2, tab3 = st.tabs(["📋 Management", "📅 Calendar View", "📄 Export Reports"])

    with tab1:
        # =================================================
        # SUMMARY METRICS
        # =================================================
        total = len(df)
        pending = len(df[df.status == "Pending"]) if not df.empty else 0
        done = len(df[df.status == "Done"]) if not df.empty else 0
        overdue = len(df[df.status == "Overdue"]) if not df.empty else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 Total", total)
        c2.metric("🟠 Pending", pending)
        c3.metric("🟢 Done", done)
        c4.metric("🔴 Overdue", overdue)

        st.markdown('<hr style="margin:5px 0; border:0; border-top:1px solid #ddd;">', unsafe_allow_html=True)

        # =================================================
        # NEW FOLLOW-UP BUTTON
        # =================================================
        if st.button("➕ New Follow-up", width="stretch"):
            st.session_state.followup_saved = False
            st.session_state.edit_followup_id = None

        # =================================================
        # ADD FOLLOW-UP FORM
        # =================================================
        if not st.session_state.followup_saved:
            with st.container(border=True):
                st.subheader("➕ Add New Follow-up")
                relation = st.selectbox("Related To", ["Lead", "Customer"], key="follow_type")

                if relation == "Lead":
                    lead_map = {}
                    if not leads.empty:
                        for row in leads.itertuples():
                            lead_map[row.id] = f"🎯 {row.contact_person} ({row.company})"
                    selected_id = st.selectbox("Select Lead", list(lead_map.keys()), format_func=lambda x: lead_map.get(x, ""), key="follow_lead")
                else:
                    customer_map = {}
                    if not customers.empty:
                        for row in customers.itertuples():
                            customer_map[row.id] = f"👥 {row.name} ({row.company})"
                    selected_id = st.selectbox("Select Customer", list(customer_map.keys()), format_func=lambda x: customer_map.get(x, ""), key="follow_customer")

                title = st.text_input("Title", key="follow_title")
                col1, col2 = st.columns(2)
                with col1:
                    follow_date = st.date_input("Follow-up Date", key="follow_date")
                with col2:
                    status = st.selectbox("Status", ["Pending", "Done", "Overdue"], key="follow_status")

                remarks = st.text_area("Remarks", key="follow_remarks")
                save = st.button("💾 Save Follow-up", width="stretch")
                if save:
                    if not title.strip():
                        st.error("Title required")
                    else:
                        add_followup(selected_id, title, str(follow_date), status, remarks)
                        st.session_state.followup_saved = True
                        clear_followup_form()
                        show_message("Follow-up saved successfully ✅")
                        st.rerun()

        st.markdown("---")

        # Replaced structural return block with conditional wrapper so subsequent tabs process
        if df.empty:
            st.info("No follow-ups found")
        else:
            # =================================================
            # SEARCH INTERFACE
            # =================================================
            search = st.text_input("🔍 Search Follow-ups")
            df_filtered = df.copy()
            if search:
                df_filtered = df_filtered[
                    df_filtered.astype(str)
                    .apply(lambda x: x.str.contains(search, case=False, na=False))
                    .any(axis=1)
                ]

            # =================================================
            # STATUS BADGE DEFINITIONS
            # =================================================
            status_badge = {
                "Pending": '<span class="status-pending">🟠 Pending</span>',
                "Done": '<span class="status-done">🟢 Done</span>',
                "Overdue": '<span class="status-overdue">🔴 Overdue</span>'
            }

            # =================================================
            # EDIT PANEL
            # =================================================
            if st.session_state.edit_followup_id:
                edit_id = st.session_state.edit_followup_id
                edit_df = df_filtered[df_filtered.id == edit_id]

                if not edit_df.empty:
                    row = edit_df.iloc[0]
                    st.markdown("---")
                    with st.container(border=True):
                        st.subheader("✏️ Edit Follow-up")
                        new_title = st.text_input("Title", value=row["title"], key=f"edit_title_{edit_id}")
                        new_date = st.date_input("Follow-up Date", value=pd.to_datetime(row["followup_date"]), key=f"edit_date_{edit_id}")
                        new_status = st.selectbox(
                            "Status",
                            ["Pending", "Done", "Overdue"],
                            index=["Pending", "Done", "Overdue"].index(row["status"]),
                            key=f"edit_status_{edit_id}"
                        )
                        new_remarks = st.text_area("Remarks", value=row["remarks"], key=f"edit_remarks_{edit_id}")

                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("💾 Update Follow-up", key=f"update_{edit_id}", width="stretch"):
                                update_followup(edit_id, row["lead_id"], new_title, str(new_date), new_status, new_remarks)
                                st.session_state.edit_followup_id = None
                                show_message("Follow-up updated successfully ✅")
                                st.rerun()
                        with c2:
                            if st.button("❌ Cancel", key=f"cancel_{edit_id}", width="stretch"):
                                st.session_state.edit_followup_id = None
                                st.rerun()

            # =================================================
            # EXPORT CSV BUTTON
            # =================================================
            st.markdown("---")
            csv = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download Follow-ups", csv, "followups.csv", "text/csv", width="stretch")
            st.markdown("---")

            # =================================================
            # TABLE HEADER RENDERING
            # =================================================
            st.subheader("📅 Follow-up List")
            headers = st.columns([2.5, 1.5, 1.5, 3, 1.5])
            titles = ["📌 Title", "📅 Date", "🏷 Status", "📝 Remarks", "⚙ Actions"]

            for col, title_text in zip(headers, titles):
                col.markdown(f'<div class="table-header">{title_text}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # =================================================
            # TABLE DATA ROWS
            # =================================================
            for row in df_filtered.itertuples():
                cols = st.columns([2.5, 1.5, 1.5, 3, 1.5])
                with cols[0]:
                    st.write(f"📌 {row.title}")
                with cols[1]:
                    st.write(str(row.followup_date))
                with cols[2]:
                    st.markdown(status_badge.get(row.status, str(row.status)), unsafe_allow_html=True)
                with cols[3]:
                    if row.remarks:
                        st.write(str(row.remarks))
                    else:
                        st.caption("-")
                with cols[4]:
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✏️", key=f"edit_follow_{row.id}", help="Edit Follow-up"):
                            st.session_state.edit_followup_id = row.id
                            st.rerun()
                    with b2:
                        if st.button("🗑️", key=f"delete_follow_{row.id}", help="Delete Follow-up"):
                            delete_followup(row.id)
                            show_message("Follow-up deleted 🗑️")
                            st.rerun()
                
                st.markdown('<hr style="margin:4px 0px; border:0; border-top:1px solid #eeeeee;">', unsafe_allow_html=True)

            # =================================================
            # TODAY FOLLOW-UPS ACTION PANEL
            # =================================================
            st.markdown("---")
            st.subheader("🔥 Today's Follow-ups")
            today = str(date.today())
            today_df = df_filtered[df_filtered["followup_date"] == today]

            if today_df.empty:
                st.info("No follow-ups scheduled today")
            else:
                for row in today_df.itertuples():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 2, 2])
                        with c1:
                            st.write(f"📌 {row.title}")
                        with c2:
                            st.write(str(row.followup_date))
                        with c3:
                            if st.button("✔ Mark Done", key=f"done_{row.id}", width="stretch"):
                                update_followup(row.id, row.lead_id, row.title, row.followup_date, "Done", row.remarks)
                                show_message("Marked as Done ✅")
                                st.rerun()

    with tab2:
        # =================================================
        # VISUAL INTERACTIVE CALENDAR
        # =================================================
        st.subheader("📅 Interactive Schedule")
        if not df.empty:
            events = []
            for row in df.itertuples():
                events.append({
                    "title": str(row.title),
                    "start": str(row.followup_date),
                    "backgroundColor": "#28a745" if row.status == "Done" else "#ff9800"
                })
            calendar(events=events, options={"initialView": "dayGridMonth"})
        else:
            st.info("No schedule matrix records discovered to overlay onto the timeline.")

    with tab3:
        # =================================================
        # CLEANLY ALIGNED REPORTING SYSTEM
        # =================================================
        st.subheader("📄 Export Document Assets")
        if not df.empty:
            st.write("Generate and download an cleanly structural, aligned PDF ledger copy of your customer tracking matrices.")
            pdf_data = generate_pdf(df)
            st.download_button(
                "⬇ Download PDF Report",
                data=pdf_data,
                file_name="crm_followups_report.pdf",
                mime="application/pdf",
                width="stretch"
            )
        else:
            st.warning("No operational transactional row values discovered to compile documentation reports.")
