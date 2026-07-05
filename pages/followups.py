import streamlit as st
import pandas as pd
from datetime import date

from database import add_followup, get_followups, get_leads, get_customers


def followups_page():

    st.title("📅 Follow-ups")

    # ---------------- LOAD DATA ----------------
    df = get_followups()

    if df is None:
        df = pd.DataFrame()

    # ---------------- GET LEADS + CUSTOMERS ----------------
    leads = get_leads()
    customers = get_customers()

    if leads is None:
        leads = pd.DataFrame()

    if customers is None:
        customers = pd.DataFrame()

    # Convert to dict for dropdown display
    lead_map = {}
    customer_map = {}

    if not leads.empty:
        for row in leads.itertuples():
            lead_map[row.id] = f"🎯 Lead: {row.contact_person} ({row.company})"

    if not customers.empty:
        for row in customers.itertuples():
            customer_map[row.id] = f"👥 Customer: {row.name} ({row.company})"

    # ---------------- ADD FOLLOW-UP ----------------
    with st.expander("➕ Add Follow-up"):

        type_choice = st.selectbox("Related To", ["Lead", "Customer"])

        if type_choice == "Lead":
            selected_id = st.selectbox(
                "Select Lead",
                options=list(lead_map.keys()),
                format_func=lambda x: lead_map[x]
            )
        else:
            selected_id = st.selectbox(
                "Select Customer",
                options=list(customer_map.keys()),
                format_func=lambda x: customer_map[x]
            )

        title = st.text_input("Title")

        col1, col2 = st.columns(2)

        with col1:
            followup_date = st.date_input("Follow-up Date")

        with col2:
            status = st.selectbox("Status", ["Pending", "Done", "Overdue"])

        remarks = st.text_area("Remarks")

        if st.button("Save Follow-up"):

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
                st.error("Title is required")

    st.markdown("---")

    # ---------------- DISPLAY ----------------
    if df.empty:
        st.info("No follow-ups found")
        return

    st.subheader("📅 All Follow-ups")

    st.dataframe(df, use_container_width=True)

    # ---------------- TODAY FILTER ----------------
    today = str(date.today())

    st.subheader("🔥 Today's Follow-ups")

    today_df = df[df["followup_date"] == today]

    if today_df.empty:
        st.info("No follow-ups for today")
    else:
        st.dataframe(today_df, use_container_width=True)
