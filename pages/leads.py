import streamlit as st
import pandas as pd
from database import get_leads, add_lead, delete_lead, add_customer


def leads_page():

    st.title("🎯 Leads")

    df = get_leads()
    if df is None:
        df = pd.DataFrame()

    st.subheader("➕ Add Lead")

    with st.form("add_lead"):

        company = st.text_input("Company")
        contact = st.text_input("Contact Person")
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        source = st.selectbox("Source", ["Website", "Facebook", "Referral", "Other"])
        status = st.selectbox("Status", ["New", "Contacted", "Won", "Lost"])
        followup_date = st.date_input("Follow-up Date")
        remarks = st.text_area("Remarks")
        assigned_to = st.text_input("Assign To")

        submit = st.form_submit_button("Save Lead")

        if submit and company and contact:

            add_lead(
                company, contact, phone, email,
                source, status, str(followup_date),
                remarks, assigned_to
            )

            st.success("Lead saved!")
            st.rerun()

    st.markdown("---")

    st.subheader("📋 Leads")

    if df.empty:
        st.info("No leads found")
        return

    for row in df.itertuples():

        col1, col2, col3, col4 = st.columns(4)

        col1.write(row.company)
        col2.write(row.contact_person)
        col3.write(row.status)
        col4.write(row.assigned_to)

        c1, c2 = st.columns(2)

        with c1:
            if st.button("➡ Convert", key=f"conv_{row.id}"):

                add_customer(
                    row.contact_person,
                    row.phone,
                    row.email,
                    row.company,
                    "New"
                )

                delete_lead(row.id)

                st.success("Converted to Customer")
                st.rerun()

        with c2:
            if st.button("🗑 Delete", key=f"del_{row.id}"):

                delete_lead(row.id)
                st.warning("Lead deleted")
                st.rerun()
