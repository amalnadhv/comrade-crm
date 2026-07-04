import streamlit as st
import pandas as pd

from database import (
    init_db,
    add_customer,
    get_customers,
    delete_customer,
    update_customer
)

# ---------------- INIT ----------------
init_db()

st.set_page_config(
    page_title="Comrade CRM",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
def load_df():
    rows = get_customers()
    return pd.DataFrame(rows, columns=[
        "id", "name", "phone", "email", "company", "status"
    ])

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Comrade CRM")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Customers", "Analytics"]
)

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
        st.sidebar.success("Customer added!")
        st.rerun()
    else:
        st.sidebar.error("Name and Phone required")

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("📌 Dashboard Overview")

    df = load_df()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", len(df))
    col2.metric("New Leads", len(df[df["status"] == "New"]))
    col3.metric("Won Deals", len(df[df["status"] == "Won"]))
    col4.metric("Lost Deals", len(df[df["status"] == "Lost"]))

    st.markdown("---")
    st.subheader("Recent Customers")
    st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

# ---------------- CUSTOMERS ----------------
elif page == "Customers":
    st.title("👥 Customers Management")

    df = load_df()

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

        # ---------------- DELETE ----------------
        if c6.button("🗑️", key=f"del_{row['id']}"):
            delete_customer(row["id"])
            st.rerun()

        # ---------------- EDIT ----------------
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

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📈 Analytics")

    df = load_df()

    if df.empty:
        st.info("No data yet")
    else:
        status_counts = df["status"].value_counts()
        st.bar_chart(status_counts)

        st.markdown("### Status Breakdown")
        st.write(status_counts)
