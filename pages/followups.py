import streamlit as st
import pandas as pd
from datetime import date

from database import (
    add_followup,
    get_followups,
    get_leads,
    get_customers,
    delete_followup,
    update_followup
)


def followups_page():

    st.title("📅 Follow-ups")

    # ---------------- LOAD DATA ----------------
    df = get_followups()
    if df is None:
        df = pd.DataFrame()

    leads = get_leads()
    if leads is None:
        leads = pd.DataFrame()
    else:
        leads = pd.DataFrame(leads)

    customers = get_customers()
    if customers is None:
        customers = pd.DataFrame()
    else:
        customers = pd.DataFrame(
            customers,
            columns=["id", "name", "phone", "email", "company", "status"]
        )

    # ---------------- MAPS ----------------
    lead_map = {}
    customer_map = {}

    if not leads.empty:
        for row in leads.itertuples():
            lead_map[row.id] = f"🎯 {row.contact_person} ({row.company})"

    if not customers.empty:
        for row in customers.itertuples():
            customer_map[row.id] = f"👥 {row.name} ({row.company})"

    # ---------------- ADD FOLLOW-UP ----------------
    with st.expander("➕ Add Follow-up"):

        type_choice = st.selectbox("Related To", ["Lead", "Customer"], key="add_type")

        if type_choice == "Lead":
            selected_id = st.selectbox(
                "Select Lead",
                list(lead_map.keys()),
                format_func=lambda x: lead_map[x],
                key="add_lead"
            )
        else:
            selected_id = st.selectbox(
                "Select Customer",
                list(customer_map.keys()),
                format_func=lambda x: customer_map[x],
                key="add_customer"
            )

        title = st.text_input("Title", key="add_title")

        col1, col2 = st.columns(2)

        with col1:
            followup_date = st.date_input("Date", key="add_date")

        with col2:
            status = st.selectbox(
                "Status",
                ["Pending", "Done", "Overdue"],
                key="add_status"
            )

        remarks = st.text_area("Remarks", key="add_remarks")

        if st.button("➕ Save Follow-up", key="add_btn"):

            if title.strip():

                add_followup(
                    selected_id,
                    title,
                    str(followup_date),
                    status,
                    remarks
                )

                st.success("Follow-up added!")
                st.rerun()

            else:
                st.error("Title required")

    st.markdown("---")

    # ---------------- DISPLAY ----------------
    if df.empty:
        st.info("No follow-ups found")
        return

    st.subheader("📅 All Follow-ups")

    # ---------------- EDIT STATE ----------------
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None

    for row in df.itertuples():

        col1, col2, col3, col4, col5, col6 = st.columns([1,2,2,2,2,2])

        col1.write(row.id)
        col2.write(row.lead_id)
        col3.write(row.title)
        col4.write(row.followup_date)
        col5.write(row.status)

        # ---------------- ACTIONS ----------------
        with col6:
            edit_btn, delete_btn = st.columns(2)

            # EDIT BUTTON
            with edit_btn:
                if st.button("✏️", key=f"edit_{row.id}"):
                    st.session_state.edit_id = row.id

            # DELETE BUTTON
            with delete_btn:
                if st.button("🗑", key=f"del_{row.id}"):
                    delete_followup(row.id)
                    st.rerun()

        # ---------------- EDIT PANEL ----------------
        if st.session_state.edit_id == row.id:

            st.info(f"Editing Follow-up ID: {row.id}")

            new_title = st.text_input(
                "Title",
                value=row.title,
                key=f"title_{row.id}"
            )

            new_date = st.date_input(
                "Date",
                value=pd.to_datetime(row.followup_date),
                key=f"date_{row.id}"
            )

            new_status = st.selectbox(
                "Status",
                ["Pending", "Done", "Overdue"],
                index=["Pending", "Done", "Overdue"].index(row.status),
                key=f"status_{row.id}"
            )

            new_remarks = st.text_area(
                "Remarks",
                value=row.remarks,
                key=f"remarks_{row.id}"
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("💾 Update", key=f"save_{row.id}"):

                    update_followup(
                        row.id,
                        row.lead_id,
                        new_title,
                        str(new_date),
                        new_status,
                        new_remarks
                    )

                    st.session_state.edit_id = None
                    st.success("Updated successfully!")
                    st.rerun()

            with c2:
                if st.button("❌ Cancel", key=f"cancel_{row.id}"):

                    st.session_state.edit_id = None
                    st.rerun()

    # ---------------- TODAY VIEW ----------------
    today = str(date.today())

    st.markdown("---")
    st.subheader("🔥 Today's Follow-ups")

    today_df = df[df["followup_date"] == today]

    if today_df.empty:
        st.info("No follow-ups today")
    else:
        st.dataframe(today_df, use_container_width=True)
