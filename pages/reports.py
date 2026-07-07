import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database import get_customers, get_leads, get_quotations

def reports_page():
    # --- VIBRANT CSS ---
    st.markdown("""
    <style>
        .crm-header {
            background: linear-gradient(135deg, #2563EB, #7C3AED);
            padding: 22px 30px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,.15);
        }
        .crm-title { color: white; font-size: 32px; font-weight: 800; }
        .crm-subtitle { color: #e0e7ff; font-size: 15px; margin-top: 6px; }
        .metric-card { background-color: #f8fafc; padding: 20px; border-radius: 12px; border-left: 5px solid #2563EB; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="crm-header"><div class="crm-title">📈 Analytics Dashboard</div><div class="crm-subtitle">Deep insights into your leads, customers, and revenue</div></div>', unsafe_allow_html=True)

    # --- LOAD & PREP DATA ---
    customers = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    leads = get_leads()
    quotations = get_quotations()

    # --- FILTERS ---
    st.sidebar.header("Filter Analytics")
    date_filter = st.sidebar.date_input("Filter by Date", [])
    
    # --- KPI SUMMARY ---
    st.subheader("🚀 Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", len(customers))
    c2.metric("Active Leads", len(leads))
    c3.metric("Total Quotes", len(quotations))
    c4.metric("Est. Revenue", f"AED {quotations['total'].sum():,.2f}" if not quotations.empty else "0")

    st.divider()

    # --- CHARTS SECTION ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Lead Distribution")
        if not leads.empty:
            fig_leads = px.pie(leads, names='status', hole=0.4, color_discrete_sequence=px.colors.qualitative.Vivid)
            fig_leads.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_leads, use_container_width=True)
        else:
            st.info("No data")

    with col2:
        st.subheader("💼 Customer Status")
        if not customers.empty:
            fig_cust = px.bar(customers['status'].value_counts(), orientation='h', color_discrete_sequence=['#2563EB'])
            fig_cust.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_cust, use_container_width=True)
        else:
            st.info("No data")

    # --- REVENUE TREND ---
    st.subheader("💰 Revenue Performance")
    if not quotations.empty:
        # Convert date column if necessary
        quotations['created_on'] = pd.to_datetime(quotations['created_on'])
        fig_rev = px.line(quotations, x='created_on', y='total', markers=True, color_discrete_sequence=['#7C3AED'])
        st.plotly_chart(fig_rev, use_container_width=True)
    else:
        st.info("No quotation data available")

    # --- DATA EXPORT ---
    st.divider()
    with st.expander("📥 Export & Raw Data"):
        tab1, tab2, tab3 = st.tabs(["Customers", "Leads", "Quotations"])
        with tab1:
            st.download_button("Export Customers CSV", customers.to_csv(index=False), "customers.csv")
            st.dataframe(customers, use_container_width=True)
        with tab2:
            st.download_button("Export Leads CSV", leads.to_csv(index=False), "leads.csv")
            st.dataframe(leads, use_container_width=True)
        with tab3:
            st.download_button("Export Quotations CSV", quotations.to_csv(index=False), "quotations.csv")
            st.dataframe(quotations, use_container_width=True)
