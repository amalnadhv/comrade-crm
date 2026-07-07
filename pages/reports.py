import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_customers, get_leads, get_quotations

def reports_page():
    # --- CSS Styling ---
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

    st.markdown('<div class="crm-header"><div class="crm-title">🚀 Sales Pipeline Funnel</div><div class="crm-subtitle">Visualizing your customer conversion journey</div></div>', unsafe_allow_html=True)

    # --- Load Data ---
    customers = pd.DataFrame(get_customers(), columns=["id", "name", "phone", "email", "company", "status"])
    leads = get_leads()
    quotations = get_quotations()

    # --- Calculate Funnel Data ---
    # Adjust logic below if your database structure differs
    total_leads = len(leads) if leads is not None else 0
    total_customers = len(customers)
    # Count quotes where customer_name exists
    total_quotes = len(quotations) if quotations is not None else 0
    # Count quotes with 'Approved' or 'Success' status
    success_quotes = len(quotations[quotations['status'] == 'Approved']) if quotations is not None else 0

    # Create the Funnel DataFrame
    funnel_df = pd.DataFrame({
        "Stage": ["Total Leads", "Customers", "Quotations", "Successful Sales"],
        "Count": [total_leads, total_customers, total_quotes, success_quotes]
    })

    # --- Funnel Chart ---
    st.subheader("🎯 Conversion Overview")
    
    fig = px.funnel(
        funnel_df, 
        x='Count', 
        y='Stage', 
        color='Stage',
        color_discrete_sequence=['#2563EB', '#4F46E5', '#7C3AED', '#EC4899']
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- KPI Cards ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads", total_leads)
    c2.metric("Customers", total_customers)
    c3.metric("Quotes", total_quotes)
    c4.metric("Success", success_quotes)
