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

    # ---------------- LOAD FOLLOWUPS ----------------
    df = get_followups()
    if df is None:
        df = pd.DataFrame()

    # ---------------- LOAD LEADS ----------------
    leads = get_leads()
    if leads is None:
        leads = pd.DataFrame()
    else:
        leads = pd.DataFrame(leads)

    # ---------------- LOAD CUSTOMERS ----------------
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

        type_choice = st.selectbox("Related To", ["Lead", "Customer"], key="type_add")

        if type_choice == "Lead" and lead_map:
            selected_id = st.selectbox(
                "Select Lead",
                list(lead_map.keys()),
                format_func=lambda x: lead_map[x],
                key="lead_add"
            )
        elif type_choice == "Customer" and customer_map:
            selected_id = st.selectbox(
                "Select Customer",
                list(customer_map.keys()),
                format_func=lambda x: customer_map[x],
                key="customer_add"
            )
        else:
            st.warning("No data available")
            return

        title = st.text_input("Title", key="title_add")

        col1, col2 = st.columns(2)

        with col1:
            followup_date = st.date_input("Date", key="date_add")

        with col2:
            status = st.selectbox(
                "Status",
                ["Pending", "Done", "Overdue"],
                key="status_add"
            )

        remarks = st.text_area("Remarks", key="remarks_add")

        if st.button("➕ Save Follow-up", key="save_add"):

            if title:
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

    for row in df.itertuples():

        col1, col2, col3, col4, col5, col6 = st.columns([1,2,2,2,2,2])

        col1.write(row.id)
        col2.write(row.lead_id)
        col3.write(row.title)
        col4.write(row.followup_date)
        col5.write(row.status)

        # ---------------- ACTIONS ----------------
        with col6:
            edit_col, delete_col = st.columns(2)

            # ---------------- EDIT ----------------
            with edit_col:

                if st.button("✏️", key=f"edit_btn_{row.id}"):

                    st.session_state[f"edit_{row.id}"] = True

            if st.session_state.get(f"edit_{row.id}", False):

                st.info(f"Editing Follow-up ID: {row.id}")

                new_title = st.text_input(
                    "Title",
                    row.title,
                    key=f"title_{row.id}"
                )

                new_date = st.date_input(
                    "Date",
                    pd.to_datetime(row.followup_date),
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
                    row.remarks,
                    key=f"remarks_{row.id}"
                )

                col_save, col_cancel = st.columns(2)

                with col_save:
                    if st.button("💾 Update", key=f"save_{row.id}"):

                        update_followup(
                            row.id,
                            row.lead_id,
                            new_title,
                            str(new_date),
                            new_status,
                            new_remarks
                        )

                        st.session_state[f"edit_{row.id}"] = False
                        st.success("Updated!")
                        st.rerun()

                with col_cancel:
                    if st.button("❌ Cancel", key=f"cancel_{row.id}"):

                        st.session_state[f"edit_{row.id}"] = False
                        st.rerun()

            # ---------------- DELETE ----------------
            with delete_col:
                if st.button("🗑", key=f"del_{row.id}"):

                    delete_followup(row.id)
                    st.rerun()

    # ---------------- TODAY VIEW ----------------
    today = str(date.today())

    st.markdown("---")
    st.subheader("🔥 Today's Follow-ups")

    today_df = df[df["followup_date"] == today]

    if today_df.empty:
        st.info("No follow-ups for today")
    else:
        st.dataframe(today_df, use_container_width=True)
