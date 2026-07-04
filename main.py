elif page == "Customers":
    st.title("👥 Customers Management")

    df = pd.DataFrame(get_customers(), columns=[
        "id", "name", "phone", "email", "company", "status"
    ])

    search = st.text_input("🔎 Search")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False)
        ]

    for _, row in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([2,2,2,2,1,1])

        c1.write(row["name"])
        c2.write(row["phone"])
        c3.write(row["email"])
        c4.write(row["company"])
        c5.write(row["status"])

        if c6.button("🗑️", key=f"del_{row['id']}"):
            delete_customer(row["id"])
            st.rerun()

        with st.expander("✏️ Edit"):
            new_name = st.text_input("Name", row["name"], key=f"n_{row['id']}")
            new_phone = st.text_input("Phone", row["phone"], key=f"p_{row['id']}")
            new_email = st.text_input("Email", row["email"], key=f"e_{row['id']}")
            new_company = st.text_input("Company", row["company"], key=f"c_{row['id']}")
            new_status = st.selectbox(
                "Status",
                ["New", "Contacted", "Won", "Lost"],
                index=["New", "Contacted", "Won", "Lost"].index(row["status"]),
                key=f"s_{row['id']}"
            )

            if st.button("💾 Save", key=f"save_{row['id']}"):
                update_customer(
                    row["id"],
                    new_name,
                    new_phone,
                    new_email,
                    new_company,
                    new_status
                )
                st.success("Updated!")
                st.rerun()
