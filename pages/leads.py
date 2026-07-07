import streamlit as st
import pandas as pd

from database import (
    get_leads,
    add_lead,
    update_lead,
    delete_lead,
    add_customer
)


def leads_page():

    st.title("🎯 Leads Dashboard")

    # ---------------- SESSION ----------------

    if "lead_saved" not in st.session_state:
        st.session_state.lead_saved = False


    # ---------------- LOAD DATA ----------------

    df = get_leads()

    if df is None:
        df = pd.DataFrame()


    # ==================================================
    # EDIT LEAD SECTION
    # ==================================================

    if "edit_lead_id" in st.session_state:

        st.markdown("## ✏ Edit Lead")

        with st.container(border=True):

            col1, col2 = st.columns(2)

            with col1:

                edit_company = st.text_input(
                    "Company",
                    value=st.session_state.edit_company
                )

                edit_contact = st.text_input(
                    "Contact Person",
                    value=st.session_state.edit_contact
                )

                edit_phone = st.text_input(
                    "Phone",
                    value=st.session_state.edit_phone
                )

                edit_email = st.text_input(
                    "Email",
                    value=st.session_state.edit_email
                )


            with col2:

                edit_source = st.selectbox(
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
                    ].index(st.session_state.edit_source)
                )


                edit_status = st.selectbox(
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
                    ].index(st.session_state.edit_status)
                )


                edit_followup = st.text_input(
                    "Follow-up Date",
                    value=st.session_state.edit_followup
                )


                edit_assigned = st.text_input(
                    "Assign To",
                    value=st.session_state.edit_assigned
                )


            edit_remarks = st.text_area(
                "Remarks",
                value=st.session_state.edit_remarks
            )


            c1, c2 = st.columns(2)


            with c1:

                if st.button(
                    "💾 Update Lead",
                    use_container_width=True
                ):

                    update_lead(
                        st.session_state.edit_lead_id,
                        edit_company,
                        edit_contact,
                        edit_phone,
                        edit_email,
                        edit_source,
                        edit_status,
                        edit_followup,
                        edit_remarks,
                        edit_assigned
                    )


                    del st.session_state.edit_lead_id

                    st.success(
                        "Lead updated successfully"
                    )

                    st.rerun()


            with c2:

                if st.button(
                    "❌ Cancel",
                    use_container_width=True
                ):

                    del st.session_state.edit_lead_id

                    st.rerun()



    # ==================================================
    # ADD LEAD SECTION
    # ==================================================

    st.markdown("---")

    col1, col2 = st.columns([1,5])


    with col1:

        if st.button(
            "➕ New Lead",
            use_container_width=True
        ):

            st.session_state.lead_saved = False

            st.rerun()



    with st.expander(
        "➕ Add New Lead",
        expanded=True
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


                assigned_to = st.text_input(
                    "Assign To"
                )


            remarks = st.text_area(
                "Remarks"
            )


            save = st.form_submit_button(
                "💾 Save Lead",
                disabled=st.session_state.lead_saved
            )


            if save:


                if not company or not contact:

                    st.error(
                        "Company and Contact Person required"
                    )


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


                    st.success(
                        "Lead saved successfully"
                    )


                    st.rerun()



    # ==================================================
    # LEADS GRID
    # ==================================================

    st.markdown("---")

    st.subheader(
        "📋 All Leads"
    )


    if df.empty:

        st.info(
            "No leads found"
        )

        return



    cols_per_row = 4


    rows = [
        df.iloc[i:i + cols_per_row]
        for i in range(
            0,
            len(df),
            cols_per_row
        )
    ]



    for row_group in rows:


        cols = st.columns(
            cols_per_row
        )


        for col, row in zip(
            cols,
            row_group.itertuples()
        ):


            with col:


                with st.container(
                    border=True
                ):


                    st.markdown(
                        f"### 🏢 {row.company}"
                    )

                    st.caption(
                        f"👤 {row.contact_person}"
                    )


                    st.write(
                        f"📞 {row.phone or '-'}"
                    )

                    st.write(
                        f"🏷 {row.status}"
                    )

                    st.write(
                        f"📍 {row.assigned_to or 'Unassigned'}"
                    )


                    st.divider()



                    b1, b2, b3 = st.columns(3)


                    # Convert

                    with b1:

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
                                "Converted"
                            )

                            st.rerun()



                    # Edit

                    with b2:

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



                    # Delete

                    with b3:

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
