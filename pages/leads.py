import streamlit as st
import pandas as pd

from database import add_lead, get_leads

# ---------------- PAGE ----------------
def leads_page():

    st.title("🎯 Leads")

    # ---------------- LOAD DATA ----------------
    df = get_leads()

    # Convert to DataFrame safely
    if df is None or df.empty:
        df = pd.DataFrame(columns=[
            "id", "company", "contact_person", "phone", "email",
            "source", "status", "followup_date", "remarks"
        ])

    # ---------------- ADD LEAD ----------------
    with st.expander("➕ Add Lead"):

        col1, col2 = st.columns(2)

        with col1:
            company = st.text_input("Company")
            contact_person = st.text_input("Contact Person")
            phone = st.text_input("Phone")
            email = st.text_input("Email")

        with col2:
            source = st.selectbox(
                "Lead Source",
                ["Website", "Referral", "Facebook", "Instagram", "Cold Call", "Other"]
            )

            status = st.selectbox(
                "Status",
                ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"]
            )

            followup_date = st.date_input("Follow-up Date")
            remarks = st.text_area("Remarks")

        if st.button("Save Lead"):
            if company and phone:
                add_lead(
                    company,
                    contact_person,
                    phone,
                    email,
                    source,
                    status,
                    str(followup_date),
                    remarks
                )
                st.success("Lead added successfully!")
                st.rerun()
            else:
                st.error("Company and Phone are required")

    st.markdown("---")

    # ---------------- SEARCH ----------------
    search = st.text_input("🔍 Search leads")

    if not df.empty and search:
        df = df[
            df["company"].str.contains(search, case=False, na=False) |
            df["contact_person"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False)
        ]

    # ---------------- STATUS COLORS ----------------
    status_colors = {
        "New": "🔵 New",
        "Contacted": "🟡 Contacted",
        "Qualified": "🟠 Qualified",
        "Proposal": "🟣 Proposal",
        "Won": "🟢 Won",
        "Lost": "🔴 Lost"
    }

    # ---------------- TABLE HEADER ----------------
    st.markdown("### Lead List")

    if df.empty:
        st.info("No leads found.")
        return

    # ---------------- LEADS LIST ----------------
    for row in df.itertuples():

        col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,2,2,2])

        col1.write(row.company)
        col2.write(row.contact_person)
        col3.write(row.phone)
        col4.write(row.source)
        col5.write(status_colors.get(row.status, row.status))

        with col6:
            st.button("View", key=f"view_{row.id}")
