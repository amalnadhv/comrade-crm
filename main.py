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

    # ---------------- PROFESSIONAL STYLE ----------------
    st.markdown("""
    <style>

    /* Page spacing */
    .block-container {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Header */
    .crm-header {
        background: #0f172a;
        color: #e2e8f0;
        padding: 10px 12px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
    }

    /* Rows */
    .crm-row {
        padding: 10px 12px;
        border-bottom: 1px solid #1f2937;
        font-size: 13px;
    }

    .crm-row:hover {
        background: #111827;
    }

    /* Edit highlight */
    .edit-active {
        background: #1e293b !important;
        border-left: 3px solid #3b82f6;
    }

    /* Status badge */
    .badge {
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 11px;
        color: white;
        display: inline-block;
    }

    .New { background: #3b82f6; }
    .Contacted { background: #f59e0b; }
    .Won { background: #10b981; }
    .Lost { background: #ef4444; }

    /* Buttons (compact SaaS style) */
    button[kind="secondary"] {
        padding: 4px 8px !important;
        font-size: 12px !important;
        border-radius: 6px !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    h1, h2, h3, h4, h5, h6 = st.columns([2.2, 2.2, 3, 2.2, 1.6, 1.6])

    h1.markdown("**Name**")
    h2.markdown("**Phone**")
    h3.markdown("**Email**")
    h4.markdown("**Company**")
    h5.markdown("**Status**")
    h6.markdown("**Actions**")

    st.divider()

    # ---------------- ROWS ----------------
    for idx, row in enumerate(df.itertuples()):

        is_edit = st.session_state.get("edit_id") == row.id

        row_style = "crm-row edit-active" if is_edit else "crm-row"

        st.markdown(f"""
        <div class="{row_style}">
            <div style="display:flex; gap:10px;">
                <div style="width:18%"><b>{row.name}</b></div>
                <div style="width:18%">{row.phone}</div>
                <div style="width:25%">{row.email}</div>
                <div style="width:18%">{row.company}</div>
                <div style="width:10%">
                    <span class="badge {row.status}">{row.status}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([1,1])

        with c1:
            if st.button("Edit", key=f"edit_{row.id}"):
                st.session_state["edit_id"] = row.id

        with c2:
            if st.button("Delete", key=f"del_{row.id}"):
                delete_customer(row.id)
                st.rerun()

        # ---------------- EDIT MODE ----------------
        if st.session_state.get("edit_id") == row.id:

            st.markdown("### Edit Customer")

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
