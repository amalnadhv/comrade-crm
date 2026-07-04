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
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
    }

    .row {
        padding: 10px;
        border-radius: 8px;
        margin-top: 6px;
    }

    .even { background: #0f172a; }
    .odd { background: #111827; }

    .edit {
        border: 2px solid #3b82f6;
        background: #1f2937;
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

    button[kind="secondary"] {
        border-radius: 6px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- HEADER ----------------
    h1, h2, h3, h4, h5, h6 = st.columns([2,2,3,2,2,2])

    h1.markdown("**Name**")
    h2.markdown("**Phone**")
    h3.markdown("**Email**")
    h4.markdown("**Company**")
    h5.markdown("**Status**")
    h6.markdown("**Actions**")

    st.markdown("---")

    # ---------------- ROWS ----------------
    for idx, row in enumerate(df.itertuples()):

        is_edit = (st.session_state.get("edit_id") == row.id)

        style_class = "edit" if is_edit else ("even" if idx % 2 == 0 else "odd")

        # -------- ROW DISPLAY --------
        r1, r2, r3, r4, r5, r6 = st.columns([2,2,3,2,2,2])

        with r1:
            st.markdown(f"**{row.name}**")

        with r2:
            st.write(row.phone)

        with r3:
            st.write(row.email)

        with r4:
            st.write(row.company)

        with r5:
            st.markdown(
                f"<span class='badge {row.status}'>{row.status}</span>",
                unsafe_allow_html=True
            )

        with r6:
            b1, b2 = st.columns(2)

            with b1:
                if st.button("✏️", key=f"edit_{row.id}"):
                    st.session_state["edit_id"] = row.id

            with b2:
                if st.button("🗑️", key=f"del_{row.id}"):
                    delete_customer(row.id)
                    st.rerun()

        # ---------------- EDIT INLINE ----------------
        if st.session_state.get("edit_id") == row.id:

            e1, e2, e3, e4, e5, e6 = st.columns([2,2,3,2,2,2])

            with e1:
                new_name = st.text_input("", row.name, key=f"n{row.id}")

            with e2:
                new_phone = st.text_input("", row.phone, key=f"p{row.id}")

            with e3:
                new_email = st.text_input("", row.email, key=f"e{row.id}")

            with e4:
                new_company = st.text_input("", row.company, key=f"c{row.id}")

            with e5:
                new_status = st.selectbox(
                    "",
                    ["New", "Contacted", "Won", "Lost"],
                    index=["New", "Contacted", "Won", "Lost"].index(row.status),
                    key=f"s{row.id}"
                )

            with e6:
                c1, c2 = st.columns(2)

                with c1:
                    if st.button("💾", key=f"save_{row.id}"):
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
                    if st.button("❌", key=f"cancel_{row.id}"):
                        st.session_state["edit_id"] = None
                        st.rerun()

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📊 Analytics")

    if df.empty:
        st.info("No data available")
    else:
        st.bar_chart(df["status"].value_counts())
