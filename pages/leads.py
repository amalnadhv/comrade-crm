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

    # ---------------- PAGE STYLE ----------------

    st.markdown(
        """
        <style>

        .main-title {
            font-size:32px;
            font-weight:800;
            color:#1f4e79;
        }

        .info-box {
            padding:15px;
            border-radius:12px;
            border:1px solid #ddd;
            text-align:center;
            background:#f8f9fa;
        }

       .row-box {
            border:1px solid #e2e2e2;
            border-radius:8px;
            padding:1px 1px;
            margin-bottom:2px;
            background:#1DBFBF;
        }

        .row-box:hover {

            background:#f5fbff;

        }

        .action-edit {

            background:#ffc107;
            color:#000;
            padding:6px 12px;
            border-radius:8px;
            font-weight:bold;

        }

        .action-convert {

            background:#28a745;
            color:white;
            padding:6px 12px;
            border-radius:8px;
            font-weight:bold;

        }

        .action-delete {

            background:#dc3545;
            color:white;
            padding:6px 12px;
            border-radius:8px;
            font-weight:bold;

        }

        /* Make action buttons attractive */
        
        div.stButton > button {
        
            border-radius:10px;
            font-size:18px;
            height:38px;
            padding:0px;
        
        }
        
        
        /* Edit button */
        
        div[data-testid="column"]:has(button[key*="edit"]) button {
        
            background:#ffc107;
            color:black;
        
        }
        
        
        /* Delete */
        
        button:hover {
        
            transform:scale(1.05);
            transition:0.2s;
        
        }

        .crm-header {
        
            background: linear-gradient(
                135deg,
                #0066cc,
                #00b4db
            );
        
            padding: 20px 28px;
        
            border-radius: 14px;
        
            margin-bottom: 18px;
        
            box-shadow: 0px 5px 15px rgba(0,0,0,0.18);
        
        }
        
        
        .crm-title {
        
            color: white;
        
            font-size: 34px;
        
            font-weight: 800;
        
            line-height: 1.2;
        
        }
        
        
        .crm-subtitle {
        
            color: #eaf7ff;
        
            font-size: 15px;
        
            margin-top: 8px;
        
        }        
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="crm-header">
            <div class="crm-title">
                🎯 Leads Dashboard
            </div>
            <div class="crm-subtitle">
                Manage prospects, follow-ups and conversions efficiently
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- SESSION ----------------

    if "lead_saved" not in st.session_state:
        st.session_state.lead_saved = False


    if "edit_lead_id" not in st.session_state:
        st.session_state.edit_lead_id = None



    # ---------------- LOAD ----------------

    df = get_leads()

    if df is None:
        df = pd.DataFrame()



    # ---------------- SUMMARY ----------------

    total = len(df)

    new = len(
        df[df.status=="New"]
    ) if not df.empty else 0


    contacted = len(
        df[df.status=="Contacted"]
    ) if not df.empty else 0


    won = len(
        df[df.status=="Won"]
    ) if not df.empty else 0


    lost = len(
        df[df.status=="Lost"]
    ) if not df.empty else 0



    c1,c2,c3,c4,c5 = st.columns(5)


    with c1:
        st.metric(
            "📋 Total",
            total
        )

    with c2:
        st.metric(
            "🟢 New",
            new
        )

    with c3:
        st.metric(
            "🟡 Contacted",
            contacted
        )

    with c4:
        st.metric(
            "🔵 Won",
            won
        )

    with c5:
        st.metric(
            "🔴 Lost",
            lost
        )

        st.markdown(
            """
            <hr style="
            margin:4px 0px;
            border:0;
            border-top:1px solid #dddddd;
            ">
            """,
            unsafe_allow_html=True
        )


    # ---------------- NEW BUTTON ----------------


    if st.button(
        "➕ New Lead",
        use_container_width=True
    ):

        st.session_state.lead_saved = False
        st.session_state.edit_lead_id = None

        st.rerun()



    # ==================================================
    # EDIT SECTION
    # ==================================================

    if st.session_state.edit_lead_id:


        st.subheader(
            "✏ Edit Lead"
        )


        with st.container(border=True):

            col1,col2 = st.columns(2)


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
                    "Follow Up Date",
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


            u1,u2 = st.columns(2)


            with u1:

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


                    st.session_state.edit_lead_id=None

                    st.success(
                        "Lead updated"
                    )

                    st.rerun()



            with u2:

                if st.button(
                    "❌ Cancel",
                    use_container_width=True
                ):

                    st.session_state.edit_lead_id=None

                    st.rerun()
                        # ==================================================
    # ADD LEAD SECTION
    # ==================================================

    with st.expander(
        "➕ Add New Lead",
        expanded=False
    ):

        with st.form(
            "add_lead",
            clear_on_submit=True
        ):

            col1,col2 = st.columns(2)


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


                    st.session_state.lead_saved=True


                    st.success(
                        "Lead saved successfully"
                    )


                    st.rerun()



    st.markdown(
        """
        <hr style="
        margin:4px 0px;
        border:0;
        border-top:1px solid #dddddd;
        ">
        """,
        unsafe_allow_html=True
    )

    # ==================================================
    # CRM LISTING
    # ==================================================

    st.subheader(
        "📋 Lead Register"
    )


    if df.empty:

        st.info(
            "No leads available"
        )

        return



    # ---------------- SEARCH ----------------


    col1,col2 = st.columns(
        [3,1]
    )


    with col1:

        search = st.text_input(
            "🔍 Search",
            placeholder="Company / Contact / Phone"
        )


    with col2:

        filter_status = st.selectbox(
            "Status",
            [
                "All",
                "New",
                "Contacted",
                "Won",
                "Lost"
            ]
        )



    data=df.copy()



    if search:

        data=data[
            data.company.str.contains(
                search,
                case=False,
                na=False
            )
            |
            data.contact_person.str.contains(
                search,
                case=False,
                na=False
            )
            |
            data.phone.str.contains(
                search,
                case=False,
                na=False
            )
        ]



    if filter_status!="All":

        data=data[
            data.status==filter_status
        ]



    st.caption(
        f"Total records: {len(data)}"
    )



    # ---------------- STATUS STYLE ----------------


    def badge(status):

        colors={
            "New":"#28a745",
            "Contacted":"#ffc107",
            "Won":"#007bff",
            "Lost":"#dc3545"
        }


        return f"""
        <span style="
        background:{colors.get(status,'gray')};
        color:white;
        padding:5px 12px;
        border-radius:15px;
        font-weight:bold;
        font-size:13px;">
        {status}
        </span>
        """



    # ---------------- TABLE HEADER ----------------


    h=st.columns(
        [
            2,
            2,
            1.5,
            1.2,
            1.5,
            1.3,
            2
        ]
    )


    titles=[
        "🏢 Company",
        "👤 Contact",
        "📞 Phone",
        "Status",
        "📅 Follow Up",
        "👨 Assigned",
        "Actions"
    ]


    for c,t in zip(h,titles):

        c.markdown(
            f"**{t}**"
        )


    st.divider()



    # ---------------- ROWS ----------------


    for row in data.itertuples():


        st.markdown(
            "<div class='row-box'>",
            unsafe_allow_html=True
        )


        c=st.columns(
            [
                2,
                2,
                1.5,
                1.2,
                1.5,
                1.3,
                2
            ]
        )


        c[0].markdown(
            f"**🏢 {row.company}**"
        )


        c[1].write(
            row.contact_person
        )


        c[2].write(
            row.phone or "-"
        )


        c[3].markdown(
            badge(row.status),
            unsafe_allow_html=True
        )


        c[4].write(
            row.followup_date
        )


        c[5].write(
            row.assigned_to or "-"
        )
                # ---------------- ACTION BUTTONS ----------------

        with c[6]:

            a1, a2, a3 = st.columns(3)


            # -------- EDIT --------

            with a1:

                if st.button(
                    "✏",
                    key=f"edit_{row.id}",
                    help="Edit Lead"
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



            # -------- CONVERT --------

            with a2:

                if st.button(
                    "✔",
                    key=f"convert_{row.id}",
                    help="Convert to Customer"
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



            # -------- DELETE --------

            with a3:

                if st.button(
                    "🗑",
                    key=f"delete_{row.id}",
                    help="Delete Lead"
                ):


                    delete_lead(
                        row.id
                    )


                    st.warning(
                        "Lead deleted"
                    )


                    st.rerun()



        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )
        
