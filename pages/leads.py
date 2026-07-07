import streamlit as st
import pandas as pd

from database import (
    get_leads,
    add_lead,
    update_lead,
    delete_lead,
    add_customer
)


# ==============================
# LEADS PAGE
# ==============================

def leads_page():

    st.set_page_config(
        layout="wide"
    )

    st.title("🎯 Leads Management")


    # ---------------- SESSION ----------------

    if "lead_saved" not in st.session_state:
        st.session_state.lead_saved = False


    if "edit_lead_id" not in st.session_state:
        st.session_state.edit_lead_id = None



    # ---------------- LOAD DATA ----------------

    df = get_leads()

    if df is None:
        df = pd.DataFrame()



    # ---------------- DASHBOARD SUMMARY ----------------

    total = len(df)

    new_count = len(
        df[df["status"] == "New"]
    ) if not df.empty else 0

    contacted_count = len(
        df[df["status"] == "Contacted"]
    ) if not df.empty else 0

    won_count = len(
        df[df["status"] == "Won"]
    ) if not df.empty else 0

    lost_count = len(
        df[df["status"] == "Lost"]
    ) if not df.empty else 0



    c1, c2, c3, c4, c5 = st.columns(5)


    with c1:
        st.metric(
            "📋 Total Leads",
            total
        )

    with c2:
        st.metric(
            "🆕 New",
            new_count
        )

    with c3:
        st.metric(
            "📞 Contacted",
            contacted_count
        )

    with c4:
        st.metric(
            "🏆 Won",
            won_count
        )

    with c5:
        st.metric(
            "❌ Lost",
            lost_count
        )



    st.markdown("---")



    # ==============================
    # NEW BUTTON
    # ==============================

    if st.button(
        "➕ New Lead",
        use_container_width=True
    ):

        st.session_state.lead_saved = False
        st.session_state.edit_lead_id = None

        st.rerun()



    # ==============================
    # EDIT SECTION
    # ==============================

    if st.session_state.edit_lead_id:


        st.subheader(
            "✏ Edit Lead"
        )


        with st.container(border=True):

            col1, col2 = st.columns(2)


            with col1:

                company = st.text_input(
                    "Company",
                    st.session_state.edit_company
                )

                contact = st.text_input(
                    "Contact Person",
                    st.session_state.edit_contact
                )

                phone = st.text_input(
                    "Phone",
                    st.session_state.edit_phone
                )

                email = st.text_input(
                    "Email",
                    st.session_state.edit_email
                )



            with col2:

                source = st.selectbox(
                    "Source",
                    [
                        "Website",
                        "Facebook",
                        "Referral",
                        "Other"
                    ],
                    index=[
                        "Website",
                        "Facebook",
                        "Referral",
                        "Other"
                    ].index(
                        st.session_state.edit_source
                    )
                )


                status = st.selectbox(
                    "Status",
                    [
                        "New",
                        "Contacted",
                        "Won",
                        "Lost"
                    ],
                    index=[
                        "New",
                        "Contacted",
                        "Won",
                        "Lost"
                    ].index(
                        st.session_state.edit_status
                    )
                )


                followup = st.text_input(
                    "Follow-up Date",
                    st.session_state.edit_followup
                )


                assigned = st.text_input(
                    "Assigned To",
                    st.session_state.edit_assigned
                )



            remarks = st.text_area(
                "Remarks",
                st.session_state.edit_remarks
            )



            e1, e2 = st.columns(2)


            with e1:

                if st.button(
                    "💾 Update Lead",
                    use_container_width=True
                ):

                    update_lead(
                        st.session_state.edit_lead_id,
                        company,
                        contact,
                        phone,
                        email,
                        source,
                        status,
                        followup,
                        remarks,
                        assigned
                    )

                    st.session_state.edit_lead_id = None

                    st.success(
                        "Lead updated successfully"
                    )

                    st.rerun()



            with e2:

                if st.button(
                    "❌ Cancel",
                    use_container_width=True
                ):

                    st.session_state.edit_lead_id = None

                    st.rerun()



    # ==============================
    # ADD LEAD
    # ==============================

    with st.expander(
        "➕ Add New Lead",
        expanded=False
    ):

        with st.form(
            "add_lead",
            clear_on_submit=True
        ):

            col1, col2 = st.columns(2)


            with col1:

                company = st.text_input(
                    "Company"
                )

                contact = st.text_input(
                    "Contact Person"
                )

                phone = st.text_input(
                    "Phone"
                )

                email = st.text_input(
                    "Email"
                )


            with col2:

                source = st.selectbox(
                    "Source",
                    [
                        "Website",
                        "Facebook",
                        "Referral",
                        "Other"
                    ]
                )

                status = st.selectbox(
                    "Status",
                    [
                        "New",
                        "Contacted",
                        "Won",
                        "Lost"
                    ]
                )

                followup_date = st.date_input(
                    "Follow-up Date"
                )

                assigned = st.text_input(
                    "Assigned To"
                )


            remarks = st.text_area(
                "Remarks"
            )


            save = st.form_submit_button(
                "💾 Save Lead",
                disabled=st.session_state.lead_saved
            )


            if save:

                if company and contact:

                    add_lead(
                        company,
                        contact,
                        phone,
                        email,
                        source,
                        status,
                        str(followup_date),
                        remarks,
                        assigned
                    )


                    st.session_state.lead_saved = True

                    st.success(
                        "Lead saved successfully"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Company and Contact Person required"
                    )
                        # ==============================
    # LEADS LISTING
    # ==============================

    st.markdown("---")

    st.subheader("📋 Lead Register")


    if df.empty:

        st.info("No leads available")

        return



    # ---------------- SEARCH + FILTER ----------------

    f1, f2 = st.columns([3, 1])


    with f1:

        search = st.text_input(
            "🔍 Search Lead",
            placeholder="Search company, contact, phone..."
        )


    with f2:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "New",
                "Contacted",
                "Won",
                "Lost"
            ]
        )



    filtered = df.copy()



    if search:

        filtered = filtered[
            filtered["company"].str.contains(
                search,
                case=False,
                na=False
            )
            |
            filtered["contact_person"].str.contains(
                search,
                case=False,
                na=False
            )
            |
            filtered["phone"].str.contains(
                search,
                case=False,
                na=False
            )
        ]



    if status_filter != "All":

        filtered = filtered[
            filtered["status"] == status_filter
        ]



    st.caption(
        f"Showing {len(filtered)} leads"
    )



    # ---------------- STATUS BADGE ----------------

    def status_badge(status):

        if status == "New":
            return "🟢 NEW"

        elif status == "Contacted":
            return "🟡 CONTACTED"

        elif status == "Won":
            return "🔵 WON"

        elif status == "Lost":
            return "🔴 LOST"

        return status



    # ---------------- TABLE HEADER ----------------


    header = st.columns(
        [
            2,
            2,
            1.5,
            1.2,
            1.5,
            1.2,
            1.5
        ]
    )


    headers = [
        "🏢 Company",
        "👤 Contact",
        "📞 Phone",
        "🏷 Status",
        "📅 Follow Up",
        "👨 Assigned",
        "Actions"
    ]


    for col, text in zip(
        header,
        headers
    ):

        col.markdown(
            f"**{text}**"
        )


    st.divider()



    # ---------------- DATA ROWS ----------------


    for row in filtered.itertuples():


        cols = st.columns(
            [
                2,
                2,
                1.5,
                1.2,
                1.5,
                1.2,
                1.5
            ]
        )



        with cols[0]:

            st.markdown(
                f"**🏢 {row.company}**"
            )


        with cols[1]:

            st.write(
                row.contact_person
            )


        with cols[2]:

            st.write(
                row.phone or "-"
            )


        with cols[3]:

            st.write(
                status_badge(row.status)
            )


        with cols[4]:

            st.write(
                row.followup_date
            )


        with cols[5]:

            st.write(
                row.assigned_to or "-"
            )


        with cols[6]:

            a1, a2, a3 = st.columns(3)


            with a1:

                if st.button(
                    "✏",
                    key=f"edit_{row.id}"
                ):

                    st.session_state.edit_lead_id = row.id

                    st.session_state.edit_company = row.company
                    st.session_state.edit_contact = row.contact_person
                    st.session_state.edit_phone = row.phone
                    st.session_state.edit_email = row.email
                    st.session_state.edit_source = row.source
                    st.session_state.edit_status = row.status
                    st.session_state.edit_followup = row.followup_date
                    st.session_state.edit_remarks = row.remarks
                    st.session_state.edit_assigned = row.assigned_to


                    st.rerun()



            with a2:

                if st.button(
                    "✔",
                    key=f"convert_{row.id}"
                ):

                    add_customer(
                        row.contact_person,
                        row.phone,
                        row.email,
                        row.company,
                        "New"
                    )


                    delete_lead(
                        row.id
                    )


                    st.success(
                        "Converted to Customer"
                    )


                    st.rerun()



            with a3:

                if st.button(
                    "🗑",
                    key=f"delete_{row.id}"
                ):

                    delete_lead(
                        row.id
                    )


                    st.warning(
                        "Lead deleted"
                    )


                    st.rerun()
                    # ==============================
# CRM STYLE
# ==============================

st.markdown(
    """
    <style>

    .lead-card {
        padding: 15px;
        border-radius: 12px;
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        margin-bottom: 8px;
    }

    .lead-title {
        font-size: 18px;
        font-weight: 700;
        color: #1f4e79;
    }

    .lead-status-new {
        color: #008000;
        font-weight: bold;
    }

    .lead-status-contact {
        color: #b8860b;
        font-weight: bold;
    }

    .lead-status-won {
        color: #0066cc;
        font-weight: bold;
    }

    .lead-status-lost {
        color: #cc0000;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)
