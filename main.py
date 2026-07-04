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

    # ---------------- STYLE ----------------
    st.markdown("""
    <style>

    .header {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        padding: 10px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }

    .row {
        padding: 10px;
        border-radius: 8px;
        margin-top: 6px;
    }

    /* Zebra effect */
    .row-even { background: #0f172a; }
    .row-odd { background: #111827; }

    /* Edit highlight */
    .row-edit {
        background: #1f2937 !important;
        border: 2px solid #3b82f6;
    }

    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        color: white;
        font-size: 12px;
    }

    .New { background: #3b82f6; }
    .Contacted { background: #f59e0b; }
    .Won { background: #10b981; }
    .Lost { background: #ef4444; }

    .btn-edit button {
        background: #3b82f6 !important;
        color: white !important;
        border-radius: 6px;
    }

    .btn-delete button {
        background: #ef4444 !important;
        color: white !important;
        border-radius: 6px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    st.markdown("""
    <div class="header">
        <div style="display:flex;">
            <div style="width:18%">Name</div>
            <div style="width:15%">Phone</div>
            <div style="width:22%">Email</div>
            <div style="width:15%">Company</div>
            <div style="width:12%">Status</div>
            <div style="width:18%">Actions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- ROWS ----------------
    for idx, row in enumerate(df.itertuples()):

        is_edit = (st.session_state.get("edit_id") == row.id)

        row_class = "row-edit" if is_edit else ("row-even" if idx % 2 == 0 else "row-odd")

        st.markdown(f"""
        <div class="row {row_class}">
            <div style="display:flex;">
                <div style="width:18%">{row.name}</div>
                <div style="width:15%">{row.phone}</div>
                <div style="width:22%">{row.email}</div>
                <div style="width:15%">{row.company}</div>
                <div style="width:12%">
                    <span class="badge {row.status}">{row.status}</span>
                </div>
                <div style="width:18%">ID: {row.id}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([1,1])

        with c1:
            if st.button("✏️ Edit", key=f"edit_{row.id}"):
                st.session_state["edit_id"] = row.id

        with c2:
            if st.button("🗑️ Delete", key=f"del_{row.id}"):
                delete_customer(row.id)
                st.rerun()

        # ---------------- EDIT PANEL ----------------
        if st.session_state.get("edit_id") == row.id:

            st.markdown("### ✏️ Edit Customer")

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
                if st.button("💾 Save", key=f"save_{row.id}"):
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
                if st.button("❌ Cancel", key=f"cancel_{row.id}"):
                    st.session_state["edit_id"] = None
                    st.rerun()

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📊 Analytics")

    if df.empty:
        st.info("No data available")
    else:
        st.bar_chart(df["status"].value_counts())
