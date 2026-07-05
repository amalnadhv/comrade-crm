import streamlit as st
import pandas as pd
from database import get_leads, add_lead, delete_lead, add_customer


def leads_page():

    st.title("🎯 Leads Dashboard")

    df = get_leads()
    if df is None:
        df = pd.DataFrame()

    # ---------------- ADD LEAD ----------------
    with st.expander("➕ Add New Lead", expanded=False):

        with st.form("add_lead"):

            col1, col2 = st.columns(2)

            with col1:
                company = st.text_input("Company")
                contact = st.text_input("Contact Person")
                phone = st.text_input("Phone")
                email = st.text_input("Email")

            with col2:
                source = st.selectbox("Source", ["Website", "Facebook", "Referral", "Other"])
                status = st.selectbox("Status", ["New", "Contacted", "Won", "Lost"])
                followup_date = st.date_input("Follow-up Date")
                assigned_to = st.text_input("Assign To")

            remarks = st.text_area("Remarks")

            submit = st.form_submit_button("💾 Save Lead")

            if submit and company and contact:

                add_lead(
                    company, contact, phone, email,
                    source, status, str(followup_date),
                    remarks, assigned_to
                )

                st.success("Lead saved!")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 All Leads")

    if df.empty:
        st.info("No leads found")
        return

    for row in df.itertuples():

        company_img = f"https://ui-avatars.com/api/?name={row.company}&background=0D8ABC&color=fff&size=64"
        person_img = f"https://ui-avatars.com/api/?name={row.contact_person}&background=FF6B6B&color=fff&size=64"

        with st.container(border=True):

            # ---------------- TOP SECTION ----------------
            col_img, col_main, col_meta = st.columns([1, 4, 2])

            with col_img:
                st.image(company_img, width=60)

            with col_main:
                st.markdown(f"### 🏢 {row.company}")
                st.markdown(f"👤 **{row.contact_person}**")
                st.caption(f"📞 {row.phone or '-'} | ✉️ {row.email or '-'}")

            with col_meta:
                st.markdown(f"🏷️ **{row.status}**")
                st.caption(f"📍 {row.assigned_to or 'Unassigned'}")

                st.image(person_img, width=40)

            st.markdown("---")

            # ---------------- ACTIONS ----------------
            b1, b2, _ = st.columns([1, 1, 6])

            with b1:
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

            with b2:
                if st.button("🗑 Delete", key=f"del_{row.id}"):

                    delete_lead(row.id)
                    st.warning("Lead deleted")
                    st.rerun()
