import streamlit as st
import pandas as pd
import io
from database import (
    add_customer,
    get_customers,
    update_customer,
    delete_customer
)

# ---------------- LOAD DATA ----------------
def load_df():
    rows = get_customers()
    return pd.DataFrame(rows, columns=[
        "id", "name", "phone", "email", "company", "status"
    ])


# ---------------- PAGE ----------------
def customers_page():

    role = st.session_state.user["role"]
    
    st.title("👥 Customers")

    df = load_df()

    # ---------------- ADD CUSTOMER ----------------
    with st.expander("➕ Add Customer"):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        company = st.text_input("Company")
        status = st.selectbox("Status", ["New", "Contacted", "Won", "Lost"])

        if st.button("Save Customer"):
            if name and phone:
                add_customer(name, phone, email, company, status)
                st.success("Customer added!")
                st.rerun()
            else:
                st.error("Name and Phone required")

    st.markdown("---")

    # ---------------- SEARCH ----------------
    search = st.text_input("🔍 Search customers")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False) |
            df["email"].str.contains(search, case=False, na=False)
        ]

    # ---------------- EDIT STATE ----------------
    if "edit_id" not in st.session_state:
        st.session_state["edit_id"] = None

    # ---------------- EDIT FORM ----------------
    if st.session_state["edit_id"] is not None:

        edit_id = st.session_state["edit_id"]
        edit_row = df[df["id"] == edit_id]

        if not edit_row.empty:
            edit_row = edit_row.iloc[0]

            st.markdown("---")
            st.subheader(f"✏️ Edit Customer: {edit_row['name']}")

            new_name = st.text_input("Name", edit_row["name"])
            new_phone = st.text_input("Phone", edit_row["phone"])
            new_email = st.text_input("Email", edit_row["email"])
            new_company = st.text_input("Company", edit_row["company"])

            new_status = st.selectbox(
                "Status",
                ["New", "Contacted", "Won", "Lost"],
                index=["New", "Contacted", "Won", "Lost"].index(edit_row["status"])
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Save Changes"):
                    update_customer(
                        edit_id,
                        new_name,
                        new_phone,
                        new_email,
                        new_company,
                        new_status
                    )
                    st.session_state["edit_id"] = None
                    st.rerun()

            with col2:
                if st.button("❌ Cancel"):
                    st.session_state["edit_id"] = None
                    st.rerun()

    st.markdown("---")
    
    st.markdown("### 📤 Export Customers")
    
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="⬇ Download Customers CSV",
        data=csv,
        file_name="customers.csv",
        mime="text/csv"
    )
    
    # ---------------- TABLE VIEW ----------------
    st.subheader("Customer List")

    if df.empty:
        st.info("No customers found.")
        return

    for row in df.itertuples():

        col1, col2, col3, col4, col5, col6 = st.columns([2,2,3,2,2,2])

        col1.write(row.name)
        col2.write(row.phone)
        col3.write(row.email)
        col4.write(row.company)

        status_colors = {
            "New": "🔵 New",
            "Contacted": "🟠 Contacted",
            "Won": "🟢 Won",
            "Lost": "🔴 Lost"
        }

        col5.write(status_colors.get(row.status, row.status))

        with col6:
            c1, c2 = st.columns(2)

            with c1:
                if st.button("✏️ Edit", key=f"edit_{row.id}"):
                    st.session_state["edit_id"] = row.id
                    st.rerun()

            with c2:
             if role == "Admin":
                if st.button("🗑️ Delete", key=f"del_{row.id}"):
                    delete_customer(row.id)
                    st.rerun()
