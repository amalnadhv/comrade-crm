import streamlit as st
import pandas as pd
import os

FILE = "data.csv"

st.set_page_config(
    page_title="Comrade CRM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DATA ----------------
def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    return pd.DataFrame(columns=["Name", "Phone", "Email", "Company", "Status"])

def save_data(df):
    df.to_csv(FILE, index=False)

df = load_data()

# ---------------- SIDEBAR NAV ----------------
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
        new_row = pd.DataFrame([{
            "Name": name,
            "Phone": phone,
            "Email": email,
            "Company": company,
            "Status": status
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.sidebar.success("Customer added!")
    else:
        st.sidebar.error("Name and Phone required")

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("📌 Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", len(df))
    col2.metric("New Leads", len(df[df["Status"] == "New"]) if len(df) > 0 else 0)
    col3.metric("Won Deals", len(df[df["Status"] == "Won"]) if len(df) > 0 else 0)
    col4.metric("Lost Deals", len(df[df["Status"] == "Lost"]) if len(df) > 0 else 0)

    st.markdown("---")

    st.subheader("Recent Customers")
    st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

# ---------------- CUSTOMERS PAGE ----------------
elif page == "Customers":
    st.title("👥 Customers")

    search = st.text_input("Search by name or phone")

    filtered = df.copy()

    if search:
        filtered = df[
            df["Name"].str.contains(search, case=False, na=False) |
            df["Phone"].str.contains(search, na=False)
        ]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📈 Analytics")

    if len(df) == 0:
        st.info("No data available yet")
    else:
        status_counts = df["Status"].value_counts()

        st.bar_chart(status_counts)

        st.markdown("### Status Breakdown")

        for k, v in status_counts.items():
            st.write(f"**{k}** : {v}")
