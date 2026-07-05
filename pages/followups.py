import streamlit as st
import pandas as pd
from datetime import date

from database import add_followup, get_followups

def followups_page():

    st.title("📅 Follow-ups")

    df = get_followups()

    if df is None or df.empty:
        df = pd.DataFrame(columns=[
            "id", "lead_id", "title", "followup_date", "status", "remarks"
        ])

    # ---------------- ADD FOLLOW-UP ----------------
    with st.expander("➕ Add Follow-up"):

        col1, col2 = st.columns(2)

        with col1:
            lead_id = st.number_input("Lead ID", min_value=1, step=1)
            title = st.text_input("Title")

        with col2:
            followup_date = st.date_input("Follow-up Date")
            status = st.selectbox("Status", ["Pending", "Done", "Overdue"])
            remarks = st.text_area("Remarks")

        if st.button("Save Follow-up"):
            if title:
                add_followup(
                    lead_id,
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

    # ---------------- FILTERS ----------------
    today = str(date.today())

    if not df.empty:

        st.subheader("Today's Follow-ups")
        today_df = df[df["followup_date"] == today]
        st.dataframe(today_df, use_container_width=True)

        st.subheader("All Follow-ups")
        st.dataframe(df, use_container_width=True)

    else:
        st.info("No follow-ups found")
