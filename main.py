import streamlit as st
import pandas as pd

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
    st.title("👥 Customers")

    df = load_df()

    search = st.text_input("🔎 Search customers")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False)
        ]

    if "edit_id" not in st.session_state:
        st.session_state["edit_id"] = None

    # ---------------- HEADER (COLUMNS ONLY) ----------------
    h1, h2, h3, h4, h5, h6 = st.columns([2,2,3,2,2,2])

    h1.markdown("**Name**")
    h2.markdown("**Phone**")
    h3.markdown("**Email**")
    h4.markdown("**Company**")
    h5.markdown("**Status**")
    h6.markdown("**Actions**")

    st.markdown("---")

    # ---------------- ROWS ----------------
    for _, row in df.iterrows():

        c1, c2, c3, c4, c5, c6 = st.columns([2,2,3,2,2,2])

        with c1:
            st.markdown(f"**{row['name']}**")

        with c2:
            st.write(row["phone"])

        with c3:
            st.write(row["email"])

        with c4:
            st.write(row["company"])

        with c5:
            color = {
                "New": "#3b82f6",
                "Contacted": "#f59e0b",
                "Won": "#10b981",
                "Lost": "#ef4444"
            }.get(row["status"], "#999")

            st.markdown(
                f"<span style='background:{color};padding:4px 10px;border-radius:12px;color:white;font-size:12px'>{row['status']}</span>",
                unsafe_allow_html=True
            )

        with c6:
            b1, b2 = st.columns(2)

            with b1:
                if st.button("✏️", key=f"edit_{row['id']}"):
                    st.session_state["edit_id"] = row["id"]

            with b2:
                if st.button("🗑️", key=f"del_{row['id']}"):
                    delete_customer(row["id"])
                    st.rerun()

        # ---------------- EDIT PANEL ----------------
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
# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📊 Analytics")

    if df.empty:
        st.info("No data available")
    else:
        st.bar_chart(df["status"].value_counts())
