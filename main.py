import streamlit as st
import pandas as pd

from database import (
    init_db,
    add_customer,
    get_customers,
    update_customer,
    delete_customer
)

st.markdown("""
<style>

/* Edit button */
div.stButton > button[kind="primary"] {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 600;
}

/* Hover effect */
div.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}

/* Delete button styling using button text selector */
div.stButton > button:contains("Delete") {
    background-color: #ef4444;
    color: white;
    border-radius: 8px;
}

/* Save button */
div.stButton > button:contains("Save") {
    background-color: #10b981;
    color: white;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)

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

# ---------------- SESSION STATE ----------------
if "edit_id" not in st.session_state:
    st.session_state["edit_id"] = None

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

    # ---------------- SEARCH ----------------
    search = st.text_input("🔍 Search customers")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False) |
            df["email"].str.contains(search, case=False, na=False)
        ]

    # ---------------- AG GRID ----------------
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(sortable=True, filter=True)

    gb.configure_selection("single", use_checkbox=True)

    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=450,
        fit_columns_on_grid_load=True
    )

    # ---------------- SAFE SELECTION HANDLING ----------------
    selected = grid_response.get("selected_rows")

    if selected is None:
        selected = []
    elif isinstance(selected, dict):
        selected = [selected]

    # ---------------- ACTION PANEL ----------------
    if len(selected) > 0:
        row = selected[0]

        st.markdown("---")
        st.subheader(f"Selected: {row['name']}")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✏️ Edit Selected", key=f"edit_selected_{row['id']}"):
                st.session_state["edit_id"] = row["id"]
                st.rerun()

        with col2:
            if st.button("🗑️ Delete Selected", key=f"del_selected_{row['id']}"):
                delete_customer(row["id"])
                st.rerun()

        with col3:
            st.info(f"Phone: {row['phone']}")

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📊 Analytics")

    if df.empty:
        st.info("No data available")
    else:
        st.bar_chart(df["status"].value_counts())
