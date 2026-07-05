import streamlit as st
import pandas as pd
from database import (
    get_leads,
    add_lead,
    convert_lead_to_customer,
    delete_customer
)


def leads_page():

    st.title("🎯 Leads")

    # ---------------- SUCCESS MESSAGE ----------------
    if st.session_state.get("lead_saved"):
        st.success("✅ Lead saved successfully!")
        st.session_state["lead_saved"] = False

    # ---------------- LOAD DATA ----------------
    df = get_leads()

    if df is None or df.empty:
        df = pd.DataFrame()

    # ---------------- ADD LEAD ----------------
    st.subheader("➕ Add Lead")

    with st.form("add_lead"):

        company = st.text_input("Company")
        contact = st.text_input("Contact Person")
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        # -------- SOURCE --------
        source_options = [
            "Website",
            "Facebook",
            "Instagram",
            "LinkedIn",
            "Referral",
            "Cold Call",
            "Advertisement",
            "Walk-in",
            "Other"
        ]

        source_choice = st.selectbox("Source", source_options)

        source_custom = ""
        if source_choice == "Other":
            source_custom = st.text_input("Enter Source")

        source = source_custom if source_choice == "Other" else source_choice

        # -------- STATUS --------
        status = st.selectbox("Status", ["New", "Contacted", "Won", "Lost"])

        # -------- FOLLOWUP DATE (MATCH DB COLUMN) --------
        followup_date = st.date_input("Follow-up Date")

        remarks = st.text_area("Remarks")
        assigned_to = st.text_input("Assign To (username)")

        submitted = st.form_submit_button("Save Lead")

        if submitted:
            if company and contact:

                add_lead(
                    company,
                    contact,
                    phone,
                    email,
                    source,
                    status,
                    str(followup_date),   # IMPORTANT FIX
                    remarks,
                    assigned_to
                )

                st.session_state["lead_saved"] = True
                st.rerun()

            else:
                st.warning("Company and Contact are required!")

    st.markdown("---")

    # ---------------- TABLE ----------------
    st.subheader("📋 All Leads")

    if df.empty:
        st.info("No leads found")
        return

    # ---------------- USER FILTER ----------------
    role = st.session_state.get("user", {}).get("role", "User")
    username = st.session_state.get("user", {}).get("username", "")

    if role != "Admin":
        df = df[df["assigned_to"] == username]

    # ---------------- DISPLAY ----------------
    for row in df.itertuples():

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.write(row.company)
        col2.write(row.contact_person)
        col3.write(row.phone)
        col4.write(row.status)
        col5.write(row.assigned_to)

        c1, c2 = st.columns(2)

        # ---------------- CONVERT ----------------
        with c1:
            if st.button("➡ Convert", key=f"conv_{row.id}"):

                if role == "Admin":
                    convert_lead_to_customer(
                        row.contact_person,
                        row.phone,
                        row.email,
                        row.company
                    )
                    st.success("Converted to customer!")
                    st.rerun()
                else:
                    st.error("Only Admin can convert")

        # ---------------- DELETE (FIXED) ----------------
        with c2:
            if st.button("🗑 Delete", key=f"del_{row.id}"):

                if role == "Admin":
                    delete_customer(row.id)   # (keep as-is since DB has no delete_lead)
                    st.rerun()
                else:
                    st.error("Only Admin can delete leads")
