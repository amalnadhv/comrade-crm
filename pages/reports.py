import streamlit as st
import pandas as pd

from database import get_customers, get_leads, get_quotations


def reports_page():

    st.title("📊 Reports & Analytics")

    # ---------------- LOAD DATA ----------------
    customers = pd.DataFrame(get_customers(), columns=[
        "id", "name", "phone", "email", "company", "status"
    ])

    leads = get_leads()
    quotations = get_quotations()

    if leads is None or leads.empty:
        leads = pd.DataFrame(columns=[
            "id", "company", "contact_person", "phone", "email",
            "source", "status", "followup_date", "remarks"
        ])

    if quotations is None or quotations.empty:
        quotations = pd.DataFrame(columns=[
            "id", "customer_name", "amount", "discount",
            "tax", "total", "status", "created_on"
        ])

    # ---------------- REPORT SUMMARY ----------------
    st.subheader("📌 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("👥 Total Customers", len(customers))
    col2.metric("🎯 Total Leads", len(leads))
    col3.metric("💼 Total Quotations", len(quotations))

    st.markdown("---")

    # ---------------- LEAD STATUS REPORT ----------------
    st.subheader("🎯 Lead Status Distribution")

    if not leads.empty:
        lead_status = leads["status"].value_counts()
        st.bar_chart(lead_status)
    else:
        st.info("No lead data available")

    st.markdown("---")

    # ---------------- CUSTOMER STATUS ----------------
    st.subheader("👥 Customer Status Distribution")

    if not customers.empty:
        customer_status = customers["status"].value_counts()
        st.bar_chart(customer_status)
    else:
        st.info("No customer data available")

    st.markdown("---")

    # ---------------- REVENUE ANALYSIS ----------------
    st.subheader("💼 Quotation Revenue")

    if not quotations.empty:
        total_revenue = quotations["total"].sum()
        avg_quote = quotations["total"].mean()

        col1, col2 = st.columns(2)

        col1.metric("Total Revenue (Est.)", f"{total_revenue:.2f}")
        col2.metric("Average Quotation", f"{avg_quote:.2f}")

        st.bar_chart(quotations["total"])
    else:
        st.info("No quotation data available")

    st.markdown("---")

    # ---------------- RAW DATA ----------------
    with st.expander("📄 View Raw Data"):
        st.write("Customers")
        st.dataframe(customers)

        st.write("Leads")
        st.dataframe(leads)

        st.write("Quotations")
        st.dataframe(quotations)
