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

    st.title("📅 Follow-ups Dashboard")

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
                list(lead_map.keys()) if lead_map else [],
                format_func=lambda x: lead_map.get(x, ""),
                key="add_lead"
            )
        else:
            selected_id = st.selectbox(
                "Select Customer",
                list(customer_map.keys()) if customer_map else [],
                format_func=lambda x: customer_map.get(x, ""),
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

    if df.empty:
        st.info("No follow-ups found")
        return

    # ---------------- STATUS BADGES ----------------
    status_badge = {
        "Pending": "🟠 Pending",
        "Done": "🟢 Done",
        "Overdue": "🔴 Overdue"
    }

    # ---------------- EDIT STATE ----------------
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None

    # ---------------- GRID VIEW ----------------
    st.subheader("📅 All Follow-ups")

    cols_per_row = 3
    rows = [df.iloc[i:i + cols_per_row] for i in range(0, len(df), cols_per_row)]

    for row_group in rows:

        cols = st.columns(cols_per_row)

        for col, row in zip(cols, row_group.itertuples()):

            with col:

                with st.container(border=True):

                    # -------- HEADER --------
                    st.markdown(f"### 📌 {row.title}")

                    st.caption(f"📅 {row.followup_date}")
                    st.markdown(f"🏷️ {status_badge.get(row.status, row.status)}")

                    st.markdown(f"🔗 ID: {row.lead_id}")

                    if row.remarks:
                        st.caption(f"📝 {row.remarks}")

                    st.markdown("---")

                    # -------- ACTIONS --------
                    b1, b2 = st.columns(2)

                    with b1:
                        if st.button("✏️", key=f"edit_{row.id}"):

                            st.session_state.edit_id = row.id
                            st.rerun()

                    with b2:
                        if st.button("🗑", key=f"del_{row.id}"):

                            delete_followup(row.id)
                            st.warning("Deleted")
                            st.rerun()

    # ---------------- EDIT PANEL ----------------
    if st.session_state.edit_id is not None:

        edit_id = st.session_state.edit_id
        edit_row = df[df["id"] == edit_id]

        if not edit_row.empty:

            edit_row = edit_row.iloc[0]

            st.markdown("---")
            st.subheader("✏️ Edit Follow-up")

            new_title = st.text_input("Title", value=edit_row["title"], key=f"title_{edit_id}")

            new_date = st.date_input(
                "Date",
                value=pd.to_datetime(edit_row["followup_date"]),
                key=f"date_{edit_id}"
            )

            new_status = st.selectbox(
                "Status",
                ["Pending", "Done", "Overdue"],
                index=["Pending", "Done", "Overdue"].index(edit_row["status"]),
                key=f"status_{edit_id}"
            )

            new_remarks = st.text_area(
                "Remarks",
                value=edit_row["remarks"],
                key=f"remarks_{edit_id}"
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("💾 Update", key=f"save_{edit_id}"):

                    update_followup(
                        edit_id,
                        edit_row["lead_id"],
                        new_title,
                        str(new_date),
                        new_status,
                        new_remarks
                    )

                    st.session_state.edit_id = None
                    st.success("Updated successfully")
                    st.rerun()

            with c2:
                if st.button("❌ Cancel", key=f"cancel_{edit_id}"):

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

        cols = st.columns(3)

        for col, row in zip(cols, today_df.itertuples()):

            with col:

                with st.container(border=True):

                    st.markdown(f"### 📌 {row.title}")
                    st.markdown(f"📅 {row.followup_date}")
                    st.markdown(f"🏷️ {status_badge.get(row.status, row.status)}")

                    if st.button("✔ Mark Done", key=f"done_{row.id}"):

                        update_followup(
                            row.id,
                            row.lead_id,
                            row.title,
                            row.followup_date,
                            "Done",
                            row.remarks
                        )

                        st.success("Marked as Done")
                        st.rerun()
