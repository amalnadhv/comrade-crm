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

    if not rows:
        return pd.DataFrame(columns=["id", "name", "phone", "email", "company", "status"])

    return pd.DataFrame(
        rows,
        columns=["id", "name", "phone", "email", "company", "status"]
    )


# ---------------- MESSAGE SYSTEM ----------------
def show_message(msg):
    st.session_state["msg"] = msg
    st.session_state["msg_time"] = time.time()


def render_message():
    msg = st.session_state.get("msg")
    msg_time = st.session_state.get("msg_time")

    if msg:
        st.success(msg)

        if msg_time and time.time() - msg_time > 3:
            st.session_state["msg"] = None
            st.session_state["msg_time"] = None
            st.rerun()


# ---------------- RESET FORM ----------------
def reset_add_form():
    for k in ["add_name", "add_phone", "add_email", "add_company", "add_status"]:
        st.session_state.pop(k, None)


# ---------------- PAGE ----------------
def customers_page():

    st.title("👥 Customers")

    role = st.session_state.get("user", {}).get("role", "User")

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

        if st.button("💾 Save Customer", key="save_customer_btn"):

            if name and phone:

                add_customer(name, phone, email, company, status)

                reset_add_form()
                show_message("Customer added successfully ✅")
                st.rerun()

            else:
                show_message("Name and Phone are required ❌")
                st.rerun()

    st.markdown("---")

    # ---------------- SEARCH ----------------
    search = st.text_input("🔍 Search customers", key="customer_search")

    if search and not df.empty:
        df = df[
            df["name"].str.contains(search, case=False, na=False)
            | df["phone"].str.contains(search, case=False, na=False)
            | df["email"].str.contains(search, case=False, na=False)
        ]

    # ---------------- EDIT STATE ----------------
    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None

    # ---------------- EDIT ----------------
    if st.session_state.edit_id is not None:

        edit_row = df[df["id"] == st.session_state.edit_id]

        if not edit_row.empty:

            edit_row = edit_row.iloc[0]

            st.markdown("---")
            st.subheader(f"✏️ Edit Customer: {edit_row['name']}")

            new_name = st.text_input("Name", value=edit_row["name"], key="edit_name")
            new_phone = st.text_input("Phone", value=edit_row["phone"], key="edit_phone")
            new_email = st.text_input("Email", value=edit_row["email"], key="edit_email")
            new_company = st.text_input("Company", value=edit_row["company"], key="edit_company")

            status_list = ["New", "Contacted", "Won", "Lost"]

            new_status = st.selectbox(
                "Status",
                status_list,
                index=status_list.index(edit_row["status"]) if edit_row["status"] in status_list else 0,
                key="edit_status"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Save Changes", key="save_edit"):

                    update_customer(
                        st.session_state.edit_id,
                        new_name,
                        new_phone,
                        new_email,
                        new_company,
                        new_status
                    )

                    st.session_state.edit_id = None
                    show_message("Customer updated successfully ✅")
                    st.rerun()

            with col2:
                if st.button("❌ Cancel", key="cancel_edit"):
                    st.session_state.edit_id = None
                    st.rerun()

    st.markdown("---")

    # ---------------- EXPORT ----------------
    st.markdown("### 📤 Export Customers")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download CSV",
        data=csv,
        file_name="customers.csv",
        mime="text/csv"
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

        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 3, 2, 2, 2])

        col1.write(row.name)
        col2.write(row.phone)
        col3.write(row.email)
        col4.write(row.company)
        col5.write(status_colors.get(row.status, row.status))

        with col6:
            c1, c2 = st.columns(2)

            with c1:
                if st.button("✏️", key=f"edit_{row.id}"):
                    st.session_state.edit_id = row.id
                    st.rerun()

            with c2:
                if role == "Admin":
                    if st.button("🗑️", key=f"del_{row.id}"):

                        delete_customer(row.id)
                        show_message("Customer deleted 🗑️")
                        st.rerun()
