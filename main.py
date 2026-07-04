elif page == "Customers":
    st.title("👥 Customers")

    df = load_df()

    search = st.text_input("🔎 Search")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False)
        ]

    if "edit_id" not in st.session_state:
        st.session_state["edit_id"] = None

    # ---------------- DISPLAY AS CARDS (SAFE UI) ----------------
    for _, row in df.iterrows():

        st.markdown(
            f"""
            <div style="
                background: #111827;
                padding: 12px;
                border-radius: 10px;
                margin-bottom: 10px;
                color: white;
            ">
                <b>{row['name']}</b><br>
                📞 {row['phone']}<br>
                ✉️ {row['email']}<br>
                🏢 {row['company']}<br>
                🔖 {row['status']}
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        # ---------------- EDIT ----------------
        with c1:
            if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                st.session_state["edit_id"] = row["id"]

        # ---------------- DELETE ----------------
        with c2:
            if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                delete_customer(row["id"])
                st.rerun()

        # ---------------- EDIT FORM ----------------
        if st.session_state["edit_id"] == row["id"]:

            st.markdown("### ✏️ Edit Customer")

            new_name = st.text_input("Name", row["name"])
            new_phone = st.text_input("Phone", row["phone"])
            new_email = st.text_input("Email", row["email"])
            new_company = st.text_input("Company", row["company"])

            new_status = st.selectbox(
                "Status",
                ["New", "Contacted", "Won", "Lost"],
                index=["New", "Contacted", "Won", "Lost"].index(row["status"])
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("💾 Save", key=f"save_{row['id']}"):
                    update_customer(
                        row["id"],
                        new_name,
                        new_phone,
                        new_email,
                        new_company,
                        new_status
                    )
                    st.session_state["edit_id"] = None
                    st.rerun()

            with c2:
                if st.button("❌ Cancel", key=f"cancel_{row['id']}"):
                    st.session_state["edit_id"] = None
                    st.rerun()
