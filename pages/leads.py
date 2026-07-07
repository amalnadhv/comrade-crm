import streamlit as st
import pandas as pd
from database import get_leads, add_lead, delete_lead, add_customer


def leads_page():

    st.title("🎯 Leads Dashboard")

    # ---------------- SESSION ----------------
    if "lead_saved" not in st.session_state:
        st.session_state.lead_saved = False

    # ---------------- NEW BUTTON ----------------
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("➕ New Lead", use_container_width=True):
            st.session_state.lead_saved = False
            st.rerun()

    df = get_leads()
    if df is None:
        df = pd.DataFrame()

    # ---------------- ADD LEAD ----------------
    with st.expander("➕ Add New Lead", expanded=True):

        with st.form("add_lead", clear_on_submit=True):

            col1, col2 = st.columns(2)

            with col1:
                company = st.text_input("Company")
                contact = st.text_input("Contact Person")
                phone = st.text_input("Phone")
                email = st.text_input("Email")

            with col2:
                source = st.selectbox(
                    "Source",
                    ["Website", "Facebook", "Referral", "Other"]
                )

                status = st.selectbox(
                    "Status",
                    ["New", "Contacted", "Won", "Lost"]
                )

                followup_date = st.date_input("Follow-up Date")

                assigned_to = st.text_input("Assign To")

            remarks = st.text_area("Remarks")

            submit = st.form_submit_button(
                "💾 Save Lead",
                disabled=st.session_state.lead_saved
            )

            if submit:

                if not company.strip() or not contact.strip():
                    st.error("Company and Contact Person are required.")

                else:

                    add_lead(
                        company,
                        contact,
                        phone,
                        email,
                        source,
                        status,
                        str(followup_date),
                        remarks,
                        assigned_to
                    )

                    st.session_state.lead_saved = True

                    st.success("✅ Lead saved successfully.")

                    st.rerun()

    st.markdown("---")

    # ---------------- LEADS GRID ----------------
    st.subheader("📋 All Leads")

    if df.empty:
        st.info("No leads found")
        return

    cols_per_row = 4

    rows = [
        df.iloc[i:i + cols_per_row]
        for i in range(0, len(df), cols_per_row)
    ]

    for row_group in rows:

        cols = st.columns(cols_per_row)

        for col, row in zip(cols, row_group.itertuples()):

            company_img = (
                f"https://ui-avatars.com/api/?name={row.company}"
                "&background=0D8ABC&color=fff&size=48"
            )

            person_img = (
                f"https://ui-avatars.com/api/?name={row.contact_person}"
                "&background=FF6B6B&color=fff&size=32"
            )

            with col:

                with st.container(border=True):

                    st.image(company_img, width=38)

                    st.markdown(f"**🏢 {row.company}**")
                    st.caption(f"👤 {row.contact_person}")

                    st.markdown(f"📞 {row.phone or '-'}")
                    st.markdown(f"🏷️ {row.status}")

                    st.image(person_img, width=22)

                    st.caption(f"📍 {row.assigned_to or 'Unassigned'}")

                    st.markdown("---")

                    b1, b2 = st.columns(2)

                    with b1:

                        if st.button("✔", key=f"conv_{row.id}"):

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

                        if st.button("🗑", key=f"del_{row.id}"):

                            delete_lead(row.id)

                            st.warning("Lead deleted")

                            st.rerun()
