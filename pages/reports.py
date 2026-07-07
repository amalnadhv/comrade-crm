import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="crm-header"><div class="crm-title">📊 Business Intelligence</div><div class="crm-subtitle">Conversion Funnel & Revenue Trends</div></div>', unsafe_allow_html=True)

    # --- Load Data ---
    customers = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    leads = get_leads()
    quotations = get_quotations()

    # --- Section 1: Funnel & Revenue (Side by Side) ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🎯 Sales Funnel")
        total_leads = len(leads) if leads is not None else 0
        total_customers = len(customers)
        total_quotes = len(quotations) if quotations is not None else 0
        success_quotes = len(quotations[quotations['status'] == 'Approved']) if quotations is not None else 0

        funnel_df = pd.DataFrame({
            "Stage": ["Leads", "Customers", "Quotations", "Success"],
            "Count": [total_leads, total_customers, total_quotes, success_quotes]
        })
        
        fig_funnel = px.funnel(funnel_df, x='Count', y='Stage', color='Stage', 
                               color_discrete_sequence=px.colors.sequential.Bluered)
        fig_funnel.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with c2:
        st.subheader("📈 Revenue Trend")
        if quotations is not None and not quotations.empty:
            # Prepare Data
            quotations['created_on'] = pd.to_datetime(quotations['created_on'])
            df_rev = quotations.groupby('created_on')['total'].sum().reset_index()
            
            # Create Vibrant Line Chart
            fig_line = px.line(df_rev, x='created_on', y='total', 
                               markers=True, 
                               line_shape='spline',
                               color_discrete_sequence=['#2563EB'])
            
            # Add a colorful gradient area under the line
            fig_line.update_traces(line=dict(width=4), fill='tozeroy', fillcolor='rgba(37, 99, 235, 0.2)')
            fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis")

    # --- Section 2: KPIs ---
    st.divider()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Leads", total_leads)
    k2.metric("Customers", total_customers)
    k3.metric("Quotes", total_quotes)
    k4.metric("Revenue (Success)", f"AED {success_quotes * 1000:,.0f}") # Placeholder math

    # --- Section 3: Raw Data Tabs ---
    st.divider()
    with st.expander("📄 Export & Raw Data"):
        tab1, tab2, tab3 = st.tabs(["Customers", "Leads", "Quotations"])
        with tab1: st.dataframe(customers, use_container_width=True)
        with tab2: st.dataframe(leads, use_container_width=True)
        with tab3: st.dataframe(quotations, use_container_width=True)
