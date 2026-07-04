import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from database import (
    init_db,
    add_customer,
    get_customers,
    update_customer,
    delete_customer
)

# ---------------- INIT ----------------
init_db()

st.set_page_config(page_title="Comrade CRM", layout="wide")


# ---------------- LOAD DATA ----------------
def load_df():
    rows = get_customers()
    return pd.DataFrame(rows, columns=[
        "id", "name", "phone", "email", "company", "status"
    ])


df = load_df()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 CRM")

page = st.sidebar.radio("Navigation", ["Dashboard", "Customers", "Analytics"])

st.sidebar.markdown("---")

st.sidebar.subheader("➕ Add Customer")

name = st.sidebar.text_input("Name")
phone = st.sidebar.text_input("Phone")
email = st.sidebar.text_input("Email")
company = st.sidebar.text_input("Company")
status = st.sidebar.selectbox("Status", ["New", "Contacted", "Won", "Lost"])

if st.sidebar.button("Save Customer"):
    if name and phone:
        add_customer(name, phone, email, company, status)
        st.success("Customer added!")
        st.rerun()
    else:
        st.error("Name and Phone required")


# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("📌 Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", len(df))
    col2.metric("New", len(df[df["status"] == "New"]) if not df.empty else 0)
    col3.metric("Won", len(df[df["status"] == "Won"]) if not df.empty else 0)
    col4.metric("Lost", len(df[df["status"] == "Lost"]) if not df.empty else 0)

    st.dataframe(df, use_container_width=True)


# ---------------- CUSTOMERS ----------------

elif page == "Customers":
    st.title("Customers")

    df = load_df()

    search = st.text_input("Search customers")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False)
        ]

    if "edit_id" not in st.session_state:
        st.session_state["edit_id"] = None

    # ---------------- HEADER ----------------
      
    # ---------------- ROWS ----------------
    for row in df.itertuples():

        c1, c2, c3, c4, c5, c6 = st.columns([2,2,3,2,2,2])

        c1.write(row.name)
        c2.write(row.phone)
        c3.write(row.email)
        c4.write(row.company)

        # simple status color (minimal + clean)
        status_colors = {
            "New": "🔵 New",
            "Contacted": "🟠 Contacted",
            "Won": "🟢 Won",
            "Lost": "🔴 Lost"
        }
        c5.write(status_colors.get(row.status, row.status))

        # ACTIONS INLINE (THIS IS THE KEY FIX)
        with c6:
            col_edit, col_del = st.columns([1,1])
        
            with col_edit:
                st.button(
                    "✏️ Edit",
                    key=f"edit_{row.id}",
                    type="primary"
                )
        
            with col_del:
                st.button(
                    "🗑️ Delete",
                    key=f"del_{row.id}",
                    type="secondary"
                )

        # ---------------- EDIT ----------------
        if st.session_state.get("edit_id") == row.id:

            st.info("Editing customer")

            new_name = st.text_input("Name", row.name)
            new_phone = st.text_input("Phone", row.phone)
            new_email = st.text_input("Email", row.email)
            new_company = st.text_input("Company", row.company)

            new_status = st.selectbox(
                "Status",
                ["New", "Contacted", "Won", "Lost"],
                index=["New", "Contacted", "Won", "Lost"].index(row.status)
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Save", key=f"save_{row.id}"):
                    update_customer(
                        row.id,
                        new_name,
                        new_phone,
                        new_email,
                        new_company,
                        new_status
                    )
                    st.session_state["edit_id"] = None
                    st.rerun()

            with c2:
                if st.button("Cancel", key=f"cancel_{row.id}"):
                    st.session_state["edit_id"] = None
                    st.rerun()

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📊 Analytics")

    if df.empty:
        st.info("No data available")
    else:
        st.bar_chart(df["status"].value_counts())
