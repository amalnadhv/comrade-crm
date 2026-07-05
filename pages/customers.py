import streamlit as st
import pandas as pd
import time

from database import (
    add_customer,
    get_customers,
    update_customer,
    delete_customer
)


# ---------------- LOAD DATA ----------------
def load_df():
    rows = get_customers()
    return pd.DataFrame(
        rows,
        columns=["id", "name", "phone", "email", "company", "status"]
    )


# ---------------- PAGE ----------------
def customers_page():

    role = st.session_state.user["role"]

    st.title("👥 Customers")

    # ---------------- SUCCESS MESSAGE HANDLER ----------------
    if "message" not in st.session_state:
        st.session_state.message = None

    if "message_time" not in st.session_state:
        st.session_state.message_time = None

    def show_message(text):
        st.session_state.message = text
        st.session_state.message_time = time.time()

    def render_message():
        if st.session_state.message:
            st.success(st.session_state.message)

            # auto clear after 3 seconds
            if time.time() - st.session_state.message_time > 3:
                st.session_state.message = None
                st.session_state.message_time = None
                st.rerun()

    render_message()

    df = load_df()

    # ---------------- ADD CUSTOMER ----------------
    with st.expander("➕ Add Customer"):

        name = st.text_input("Name", key="add_name")
        phone = st.text_input("Phone", key="add_phone")
        email = st.text_input("Email", key="add_email")
        company = st.text_input("Company", key="add_company")

        status = st.selectbox(
            "Status",
            ["New", "Contacted", "Won", "Lost"],
            key="add_status"
        )

        if st.button("💾 Save Customer", key="save_customer"):

            if name and phone:
                add_customer(name, phone, email, company, status)
                show_message("Customer added successfully ✅")
                st.rerun()
            else:
                show_message("Name and Phone are required ❌")
                st.rerun()

    st.markdown("---")

    # ---------------- SEARCH ----------------
    search = st.text_input("🔍 Search customers", key="customer_search")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False)
            | df["phone"].str.contains(search, case=False, na=False)
            | df["email"].str.contains(search, case=False, na=False)
        ]

    # ---------------- EDIT STATE ----------------
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None

    # ---------------- EDIT FORM ----------------
    if st.session_state.get("edit_id") is not None:

        edit_id = st.session_state.edit_id
        edit_row = df[df["id"] == edit_id]

        if not edit_row.empty:

            edit_row = edit_row.iloc[0]

            st.markdown("---")
            st.subheader(f"✏️ Edit Customer: {edit_row['name']}")

            new_name = st.text_input(
                "Name",
                value=edit_row["name"],
                key=f"edit_name_{edit_id}"
            )

            new_phone = st.text_input(
                "Phone",
                value=edit_row["phone"],
                key=f"edit_phone_{edit_id}"
            )

            new_email = st.text_input(
                "Email",
                value=edit_row["email"],
                key=f"edit_email_{edit_id}"
            )

            new_company = st.text_input(
                "Company",
                value=edit_row["company"],
                key=f"edit_company_{edit_id}"
            )

            status_list = ["New", "Contacted", "Won", "Lost"]

            current_status = (
                edit_row["status"]
                if edit_row["status"] in status_list
                else "New"
            )

            new_status = st.selectbox(
                "Status",
                status_list,
                index=status_list.index(current_status),
                key=f"edit_status_{edit_id}"
            )

            col1, col2 = st.columns(2)

            # ---------------- SAVE ----------------
            with col1:

                if st.button("💾 Save Changes", key=f"save_edit_{edit_id}"):

                    update_customer(
                        edit_id,
                        new_name,
                        new_phone,
                        new_email,
                        new_company,
                        new_status
                    )

                    # CLEAR SCREEN COMPLETELY
                    st.session_state.edit_id = None
                    show_message("Customer updated successfully ✅")

                    st.rerun()

            # ---------------- CANCEL ----------------
            with col2:

                if st.button("❌ Cancel", key=f"cancel_edit_{edit_id}"):

                    st.session_state.edit_id = None
                    st.rerun()

    st.markdown("---")

    # ---------------- EXPORT ----------------
    st.markdown("### 📤 Export Customers")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download Customers CSV",
        data=csv,
        file_name="customers.csv",
        mime="text/csv",
        key="download_customers"
    )

    st.markdown("---")

    # ---------------- TABLE ----------------
    st.subheader("Customer List")

    if df.empty:
        st.info("No customers found.")
        return

    status_colors = {
        "New": "🔵 New",
        "Contacted": "🟠 Contacted",
        "Won": "🟢 Won",
        "Lost": "🔴 Lost"
    }

    for row in df.itertuples():

        col1, col2, col3, col4, col5, col6 = st.columns(
            [2, 2, 3, 2, 2, 2]
        )

        col1.write(row.name)
        col2.write(row.phone)
        col3.write(row.email)
        col4.write(row.company)

        col5.write(status_colors.get(row.status, row.status))

        with col6:

            c1, c2 = st.columns(2)

            with c1:

                if st.button("✏️ Edit", key=f"edit_btn_{row.id}"):

                    st.session_state.edit_id = row.id
                    st.rerun()

            with c2:

                if role == "Admin":

                    if st.button("🗑️ Delete", key=f"delete_btn_{row.id}"):

                        delete_customer(row.id)
                        show_message("Customer deleted 🗑️")
                        st.rerun()
