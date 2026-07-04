import streamlit as st
import pandas as pd
import os

FILE = "data.csv"

st.set_page_config(
    page_title="Comrade CRM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- UI HEADER ----------------
st.markdown(
    """
    <style>
    .main-title {
        font-size:40px;
        font-weight:700;
        color:#1f77b4;
    }
    .sub-text {
        font-size:16px;
        color:gray;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">📊 Comrade CRM Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Manage your customers in a simple and clean way</div>', unsafe_allow_html=True)

st.divider()

# ---------------- LOAD DATA ----------------
def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    return pd.DataFrame(columns=["Name", "Phone", "Email", "Company", "Notes"])

def save_data(df):
    df.to_csv(FILE, index=False)

df = load_data()

# ---------------- SIDEBAR INPUT ----------------
st.sidebar.header("➕ Add Customer")

name = st.sidebar.text_input("Name")
phone = st.sidebar.text_input("Phone")
email = st.sidebar.text_input("Email")
company = st.sidebar.text_input("Company")
notes = st.sidebar.text_area("Notes")

if st.sidebar.button("Save Customer"):
    if name and phone:
        new_row = pd.DataFrame([{
            "Name": name,
            "Phone": phone,
            "Email": email,
            "Company": company,
            "Notes": notes
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.sidebar.success("Customer added!")
    else:
        st.sidebar.error("Name and Phone are required")

# ---------------- STATS CARDS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", len(df))
col2.metric("Companies", df["Company"].nunique() if len(df) > 0 else 0)
col3.metric("Emails", df["Email"].notna().sum())

st.divider()

# ---------------- SEARCH ----------------
st.subheader("🔎 Search Customers")
search = st.text_input("Type name or phone")

filtered = df.copy()

if search:
    filtered = df[
        df["Name"].str.contains(search, case=False, na=False) |
        df["Phone"].str.contains(search, na=False)
    ]

# ---------------- TABLE ----------------
st.subheader("📋 Customer Database")
st.dataframe(filtered, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Comrade CRM • Built with Streamlit")
