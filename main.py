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

    # ---------------- STYLE (ODOO LIKE) ----------------
    st.markdown("""
    <style>
    .crm-header, .crm-row {
        display: flex;
        padding: 10px;
        border-bottom: 1px solid #2b2b2b;
        font-size: 14px;
    }

    .crm-header {
        font-weight: bold;
        background: #111827;
        border-radius: 6px;
        margin-bottom: 5px;
    }

    .col-name { width: 18%; }
    .col-phone { width: 15%; }
    .col-email { width: 22%; }
    .col-company { width: 15%; }
    .col-status { width: 12%; }
    .col-actions { width: 18%; }

    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        color: white;
        display: inline-block;
    }

    .New { background: #3b82f6; }
    .Contacted { background: #f59e0b; }
    .Won { background: #10b981; }
    .Lost { background: #ef4444; }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    st.markdown("""
    <div class="crm-header">
        <div class="col-name">Name</div>
        <div class="col-phone">Phone</div>
        <div class="col-email">Email</div>
        <div class="col-company">Company</div>
        <div class="col-status">Status</div>
        <div class="col-actions">Actions</div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- ROWS ----------------
    for _, row in df.iterrows():

        status_class = row["status"]

        st.markdown(f"""
        <div class="crm-row">
            <div class="col-name">{row['name']}</div>
            <div class="col-phone">{row['phone']}</div>
            <div class="col-email">{row['email']}</div>
            <div class="col-company">{row['company']}</div>
            <div class="col-status">
                <span class="badge {status_class}">
                    {row['status']}
                </span>
            </div>
            <div class="col-actions">ID: {row['id']}</div>
        </div>
        """, unsafe_allow_html=True)

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
                    
# ================= ANALYTICS =================
elif page == "Analytics":
    st.title("Analytics")

    df = load_df()

    if df.empty:
        st.info("No data")
    else:
        st.bar_chart(df["status"].value_counts())
