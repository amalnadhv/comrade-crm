import streamlit as st
import pandas as pd

from database import (
    init_db,
    get_customers,
    add_customer,
    update_customer,
    delete_customer
)

# ---------------- INIT ----------------
init_db()

st.set_page_config(
    page_title="Comrade CRM",
    layout="wide"
)

# ---------------- LOAD DATA FUNCTION ----------------
def load_df():
    rows = get_customers()
    return pd.DataFrame(rows, columns=[
        "id", "name", "phone", "email", "company", "status"
    ])

# ---------------- SESSION STATE ----------------
if "selected_customer" not in st.session_state:
    st.session_state["selected_customer"] = None

if "edit_id" not in st.session_state:
    st.session_state["edit_id"] = None

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

# ================= DASHBOARD =================
if page == "Dashboard":
    st.title("📊 Dashboard")

    df = load_df()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", len(df))
    col2.metric("New Leads", len(df[df["status"] == "New"]))
    col3.metric("Won Deals", len(df[df["status"] == "Won"]))
    col4.metric("Lost Deals", len(df[df["status"] == "Lost"]))

    st.markdown("---")

    st.subheader("Status Chart")

    if len(df) > 0:
        st.bar_chart(df["status"].value_counts())

    st.markdown("---")

    st.subheader("Recent Customers")
    st.dataframe(df.tail(10), use_container_width=True)

# ================= CUSTOMERS =================
elif page == "Customers":
    st.title("👥 Customers")

    df = load_df()

    search = st.text_input("🔎 Search")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["phone"].str.contains(search, case=False, na=False)
        ]

    col_left, col_right = st.columns([2, 3])

    # ---------------- LEFT LIST ----------------
    with col_left:
        st.subheader("Customer List")

        for _, row in df.iterrows():

            if st.button(f"👤 {row['name']}", key=f"select_{row['id']}"):
                st.session_state["selected_customer"] = row["id"]

            st.markdown(
                f"""
                <div style="
                    background: rgba(30,41,59,0.5);
                    padding: 10px;
                    border-radius: 10px;
                    margin-bottom: 8px;
                ">
                    📞 {row['phone']} <br>
                    🔖 {row['status']}
                </div>
                """,
                unsafe_allow_html=True
            )

    # ---------------- RIGHT DETAILS ----------------
    with col_right:
        st.subheader("Customer Details")

        selected_id = st.session_state["selected_customer"]

        if selected_id is None:
            st.info("Select a customer from the left")
        else:
            customer = df[df["id"] == selected_id]

            if not customer.empty:
                customer = customer.iloc[0]

                st.markdown("### Profile")

                st.write(f"**Name:** {customer['name']}")
                st.write(f"**Phone:** {customer['phone']}")
                st.write(f"**Email:** {customer['email']}")
                st.write(f"**Company:** {customer['company']}")
                st.write(f"**Status:** {customer['status']}")

                st.markdown("---")

                c1, c2 = st.columns(2)

                # ---------------- EDIT ----------------
                with c1:
                    if st.button("✏️ Edit", key=f"edit_{customer['id']}"):
                        st.session_state["edit_id"] = customer["id"]

                # ---------------- DELETE ----------------
                with c2:
                    if st.button("🗑️ Delete", key=f"del_{customer['id']}"):
                        delete_customer(customer["id"])
                        st.session_state["selected_customer"] = None
                        st.rerun()

                # ---------------- EDIT FORM ----------------
                if st.session_state["edit_id"] == customer["id"]:

                    st.markdown("### Edit Customer")

                    new_name = st.text_input("Name", customer["name"])
                    new_phone = st.text_input("Phone", customer["phone"])
                    new_email = st.text_input("Email", customer["email"])
                    new_company = st.text_input("Company", customer["company"])

                    new_status = st.selectbox(
                        "Status",
                        ["New", "Contacted", "Won", "Lost"],
                        index=["New", "Contacted", "Won", "Lost"].index(customer["status"])
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button("💾 Save"):
                            update_customer(
                                customer["id"],
                                new_name,
                                new_phone,
                                new_email,
                                new_company,
                                new_status
                            )
                            st.session_state["edit_id"] = None
                            st.rerun()

                    with c2:
                        if st.button("❌ Cancel"):
                            st.session_state["edit_id"] = None
                            st.rerun()

# ================= ANALYTICS =================
elif page == "Analytics":
    st.title("📈 Analytics")

    df = load_df()

    if df.empty:
        st.info("No data available")
    else:
        st.bar_chart(df["status"].value_counts())
