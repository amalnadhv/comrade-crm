import streamlit as st
import pandas as pd

from database import (
    init_db,
    add_customer,
    update_customer,
    delete_customer,
    load_customers_df
)

# ---------------- INIT ----------------
init_db()

st.set_page_config(page_title="Comrade CRM", layout="wide")


# ---------------- LOAD DATA ----------------
def load_df():
    return load_customers_df()


# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Comrade CRM")

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
        st.error("Name & Phone required")


# ================= DASHBOARD =================
if page == "Dashboard":
    st.title("Dashboard")

    df = load_df()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", len(df))
    col2.metric("New", len(df[df["status"] == "New"]) if not df.empty else 0)
    col3.metric("Won", len(df[df["status"] == "Won"]) if not df.empty else 0)
    col4.metric("Lost", len(df[df["status"] == "Lost"]) if not df.empty else 0)

    st.markdown("---")

    st.dataframe(df, use_container_width=True)


# ================= CUSTOMERS =================
elif page == "Customers":
    st.title("Customers")

    df = load_df()

    search = st.text_input("🔎 Search")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False)
        ]

    if "edit_id" not in st.session_state:
        st.session_state["edit_id"] = None

    for _, row in df.iterrows():

        st.write("---")

        st.write("**Name:**", row["name"])
        st.write("**Phone:**", row["phone"])
        st.write("**Email:**", row["email"])
        st.write("**Company:**", row["company"])
        st.write("**Status:**", row["status"])

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

            st.markdown("### Edit Customer")

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


# ================= ANALYTICS =================
elif page == "Analytics":
    st.title("Analytics")

    df = load_df()

    if df.empty:
        st.info("No data")
    else:
        st.bar_chart(df["status"].value_counts())
