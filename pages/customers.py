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


# ---------------- MESSAGE SYSTEM ----------------
def show_message(msg):
    st.session_state["msg"] = msg
    st.session_state["msg_time"] = time.time()


def render_message():
    if st.session_state.get("msg"):
        st.success(st.session_state["msg"])

        if time.time() - st.session_state["msg_time"] > 3:
            st.session_state["msg"] = None
            st.session_state["msg_time"] = None
            st.rerun()


# ---------------- RESET ADD FORM ----------------
def reset_add_form():
    keys = ["add_name", "add_phone", "add_email", "add_company", "add_status"]
    for k in keys:
        st.session_state.pop(k, None)


# ---------------- PAGE ----------------
def customers_page():

    role = st.session_state.user["role"]

    st.title("👥 Customers")

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

                reset_add_form()
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
            | df["company"].str.contains(search, case=False, na=False)
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

            new_name = st.text_input("Name", value=edit_row["name"], key=f"edit_name_{edit_id}")
            new_phone = st.text_input("Phone", value=edit_row["phone"], key=f"edit_phone_{edit_id}")
            new_email = st.text_input("Email", value=edit_row["email"], key=f"edit_email_{edit_id}")
            new_company = st.text_input("Company", value=edit_row["company"], key=f"edit_company_{edit_id}")

            status_list = ["New", "Contacted", "Won", "Lost"]

            current_status = edit_row["status"] if edit_row["status"] in status_list else "New"

            new_status = st.selectbox(
                "Status",
                status_list,
                index=status_list.index(current_status),
                key=f"edit_status_{edit_id}"
            )

            col1, col2 = st.columns(2)

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

                    st.session_state.edit_id = None
                    show_message("Customer updated successfully ✅")
                    st.rerun()

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

    # ---------------- MODERN GRID VIEW ----------------
    st.subheader("👥 Customer List")

    if df.empty:
        st.info("No customers found.")
        return

    cols_per_row = 4
    rows = [df.iloc[i:i + cols_per_row] for i in range(0, len(df), cols_per_row)]

    status_badge = {
        "New": "🔵 New",
        "Contacted": "🟠 Contacted",
        "Won": "🟢 Won",
        "Lost": "🔴 Lost"
    }

    for row_group in rows:

        cols = st.columns(cols_per_row)

        for col, row in zip(cols, row_group.itertuples()):

            avatar = f"https://ui-avatars.com/api/?name={row.name}&background=0D8ABC&color=fff&size=48"

            with col:

                with st.container(border=True):

                    # -------- HEADER --------
                    st.image(avatar, width=38)
                    st.markdown(f"**👤 {row.name}**")
                    st.caption(f"🏢 {row.company}")

                    # -------- DETAILS --------
                    st.markdown(f"📞 {row.phone}")
                    st.markdown(f"✉️ {row.email}")
                    st.markdown(f"🏷️ {status_badge.get(row.status, row.status)}")

                    st.markdown("---")

                    # -------- ACTIONS --------
                    b1, b2 = st.columns(2)

                    with b1:
                        if st.button("✏️", key=f"edit_btn_{row.id}"):

                            st.session_state.edit_id = row.id
                            st.rerun()

                    with b2:
                        if role == "Admin":
                            if st.button("🗑️", key=f"del_btn_{row.id}"):

                                delete_customer(row.id)
                                show_message("Customer deleted 🗑️")
                                st.rerun()
