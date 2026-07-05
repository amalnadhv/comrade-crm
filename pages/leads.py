import streamlit as st
import pandas as pd
from database import (
    get_leads,
    add_lead,
    convert_lead_to_customer,
    delete_lead
)


def leads_page():

    st.title("🎯 Leads")

    # ---------------- SUCCESS MESSAGE ----------------
    if st.session_state.get("lead_saved"):
        st.success("✅ Lead saved successfully!")
        st.session_state["lead_saved"] = False

    # ---------------- LOAD DATA ----------------
    df = get_leads()

    if df is None:
        df = pd.DataFrame()

    # ---------------- ADD LEAD ----------------
    st.subheader("➕ Add Lead")

    with st.form("add_lead"):
        company = st.text_input("Company")
        contact = st.text_input("Contact Person")
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        # -------- SOURCE (Dropdown + Custom) --------
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

        # -------- DATE PICKER --------
        followup = st.date_input("Follow-up Date")

        remarks = st.text_area("Remarks")
        assigned_to = st.text_input("Assign To (username)")

        submitted = st.form_submit_button("Save Lead")

        if submitted:
            add_lead(
                company,
                contact,
                phone,
                email,
                source,
                status,
                str(followup),
                remarks,
                assigned_to
            )

            st.session_state["lead_saved"] = True
            st.rerun()

    st.markdown("---")

    # ---------------- TABLE ----------------
    st.subheader("📋 All Leads")

    if df.empty:
        st.info("No leads found")
        return

    # ---------------- ROLE ----------------
    role = st.session_state.user["role"]
    username = st.session_state.user["username"]

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
                    st.error("Only Admin can convert leads")

        # ---------------- DELETE ----------------
        with c2:
            if st.button("🗑 Delete", key=f"del_{row.id}"):

                if role == "Admin":
                    delete_lead(row.id)
                    st.rerun()
                else:
                    st.error("Only Admin can delete leads")
