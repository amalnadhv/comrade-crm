import streamlit as st
import pandas as pd
from database import get_customers, get_leads, get_followups
from datetime import date


def dashboard_page():

    st.title("📊 Dashboard")

    # ---------------- FILTER (INSIDE FUNCTION) ----------------
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date.today())

    # ---------------- LOAD DATA ----------------
    customers = pd.DataFrame(get_customers(), columns=[
        "id", "name", "phone", "email", "company", "status"
    ])

    leads = get_leads()
    if leads is None:
        leads = pd.DataFrame()

    followups = get_followups()
    if followups is None:
        followups = pd.DataFrame()

    # ---------------- SAFE CHECK ----------------
    if not leads.empty:
        leads = leads[leads["status"].notna()]

    # ---------------- KPIs ----------------
    total_customers = len(customers)
    total_leads = len(leads)

    won_leads = len(leads[leads["status"] == "Won"]) if not leads.empty else 0
    lost_leads = len(leads[leads["status"] == "Lost"]) if not leads.empty else 0
    pending_followups = len(followups[followups["status"] == "Pending"]) if not followups.empty else 0

    conversion_rate = round((won_leads / total_leads) * 100, 2) if total_leads > 0 else 0

    # ---------------- KPI CARDS ----------------
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("👥 Customers", total_customers)
    col2.metric("🎯 Leads", total_leads)
    col3.metric("🏆 Won", won_leads)
    col4.metric("❌ Lost", lost_leads)
    col5.metric("📅 Follow-ups", pending_followups)

    st.markdown("---")

    st.metric("📈 Conversion Rate", f"{conversion_rate}%")

    st.markdown("---")

    # ---------------- RECENT LEADS ----------------
    st.subheader("🆕 Recent Leads")

    if not leads.empty:
        st.dataframe(leads.tail(5), use_container_width=True)
    else:
        st.info("No leads available")

    # ---------------- FOLLOWUPS ----------------
    st.subheader("📅 Upcoming Follow-ups")

    if not followups.empty:
        st.dataframe(followups.head(5), use_container_width=True)
    else:
        st.info("No follow-ups scheduled")
