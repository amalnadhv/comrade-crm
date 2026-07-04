import streamlit as st
import pandas as pd

st.markdown("""
<style>
/* Sidebar radio selected item */
div[data-testid="stSidebar"] label[data-baseweb="radio"] div {
    color: #cbd5e1;
}

/* Selected radio button highlight */
div[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
    background-color: rgba(99, 102, 241, 0.25);
    border-radius: 10px;
    padding: 6px 10px;
}

/* Hover effect for sidebar items */
div[data-testid="stSidebar"] label:hover {
    background-color: rgba(148, 163, 184, 0.15);
    border-radius: 10px;
}

/* Selected button / active state feel */
.stButton button:active {
    background: rgba(99, 102, 241, 0.3) !important;
}

/* Optional: selected table row feel (approx) */
.row-highlight {
    background-color: rgba(99, 102, 241, 0.15);
    border-left: 3px solid #6366f1;
    padding: 8px;
    border-radius: 8px;
}

/* Background (deep slate) */
.stApp {
    background: linear-gradient(135deg, #0b1220, #0f172a);
    color: #e5e7eb;
}

/* Sidebar (slightly lighter for contrast) */
section[data-testid="stSidebar"] {
    background: #111c33;
}

/* Titles */
h1, h2, h3 {
    color: #f9fafb;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #1e293b, #111827);
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    border-left: 4px solid #6366f1;
}

/* Buttons (modern gradient with accent) */
.stButton button {
    background: linear-gradient(90deg, #f97316, #ef4444);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 7px 14px;
    font-weight: 600;
    transition: all 0.2s ease-in-out;
}

/* Button hover effect */
.stButton button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #ef4444, #f97316);
}

/* Input fields */
input, textarea {
    background-color: #0f172a !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
    border: 1px solid #334155 !important;
}

/* Table style */
.dataframe {
    background-color: #0f172a !important;
    color: #e5e7eb !important;
}

</style>
""", unsafe_allow_html=True)

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

    # ---------------- SEARCH ----------------
    search = st.text_input("🔎 Search by name or phone")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False)
        ]

    st.markdown("---")

    # ---------------- LIST CUSTOMERS ----------------
    for _, row in df.iterrows():

        # -------- CARD STYLE --------
        with st.container():
            st.markdown(
                """
                <div style="
                    background: rgba(30, 41, 59, 0.6);
                    padding: 12px;
                    border-radius: 12px;
                    margin-bottom: 10px;
                ">
                </div>
                """,
                unsafe_allow_html=True
            )

            c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 2, 1])

            c1.markdown(f"**{row['name']}**")
            c2.write(row["phone"])
            c3.write(row["email"])
            c4.write(row["company"])
            c5.write(row["status"])

            # ---------------- ACTIONS ----------------
            a1, a2 = st.columns([1, 1])

            # DELETE
            with a1:
                if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                    delete_customer(row["id"])
                    st.rerun()

            # EDIT TOGGLE
            with a2:
                if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                    st.session_state[f"edit_{row['id']}"] = True

        # ---------------- EDIT PANEL ----------------
        if st.session_state.get(f"edit_{row['id']}", False):

            st.markdown("### ✏️ Edit Customer")

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

            c_save, c_cancel = st.columns(2)

            # SAVE
            with c_save:
                if st.button("💾 Save", key=f"save_{row['id']}"):
                    update_customer(
                        row["id"],
                        new_name,
                        new_phone,
                        new_email,
                        new_company,
                        new_status
                    )
                    st.session_state[f"edit_{row['id']}"] = False
                    st.success("Updated successfully!")
                    st.rerun()

            # CANCEL
            with c_cancel:
                if st.button("❌ Cancel", key=f"cancel_{row['id']}"):
                    st.session_state[f"edit_{row['id']}"] = False
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
