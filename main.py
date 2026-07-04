import streamlit as st
import pandas as pd
import os

FILE = "data.csv"

st.set_page_config(page_title="Comrade CRM", layout="wide")

# ---------------- LOAD DATA ----------------
def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    return pd.DataFrame(columns=["Name", "Phone", "Email", "Company", "Notes"])

def save_data(df):
    df.to_csv(FILE, index=False)

df = load_data()

# ---------------- HEADER ----------------
st.markdown(
    """
    <div style="padding:15px;background:#1f77b4;border-radius:10px">
        <h1 style="color:white;margin:0">📊 Comrade CRM</h1>
        <p style="color:#e0e0e0;margin:0">Simple customer management system</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ---------------- SIDEBAR ----------------
st.sidebar.title("➕ Add Customer")

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
        st.sidebar.success("Saved successfully!")
    else:
        st.sidebar.error("Name and Phone required")

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("👥 Customers", len(df))
col2.metric("🏢 Companies", df["Company"].nunique() if len(df) > 0 else 0)
col3.metric("📧 Emails", df["Email"].notna().sum())

st.write("")

# ---------------- SEARCH ----------------
search = st.text_input("🔎 Search customers")

filtered = df.copy()

if search:
    filtered = df[
        df["Name"].str.contains(search, case=False, na=False) |
        df["Phone"].str.contains(search, na=False)
    ]

# ---------------- TABLE ----------------
st.subheader("Customer List")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© Comrade CRM • Streamlit App")
