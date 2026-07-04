import streamlit as st
import pandas as pd
import os

FILE = "data.csv"

st.set_page_config(page_title="Comrade CRM", layout="wide")

st.title("📊 Comrade CRM System")

# ---------------------------
# Load data
# ---------------------------
def load_data():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    else:
        return pd.DataFrame(columns=[
            "Name", "Phone", "Email", "Company", "Notes"
        ])

def save_data(df):
    df.to_csv(FILE, index=False)

df = load_data()

# ---------------------------
# Add Customer
# ---------------------------
st.sidebar.header("➕ Add New Customer")

name = st.sidebar.text_input("Name")
phone = st.sidebar.text_input("Phone")
email = st.sidebar.text_input("Email")
company = st.sidebar.text_input("Company")
notes = st.sidebar.text_area("Notes")

if st.sidebar.button("Save Customer"):
    new_data = pd.DataFrame([{
        "Name": name,
        "Phone": phone,
        "Email": email,
        "Company": company,
        "Notes": notes
    }])

    df = pd.concat([df, new_data], ignore_index=True)
    save_data(df)
    st.sidebar.success("Customer added successfully!")

# ---------------------------
# Show Data
# ---------------------------
st.subheader("📋 Customer List")
st.dataframe(df, use_container_width=True)

# ---------------------------
# Search
# ---------------------------
st.subheader("🔎 Search Customer")

search = st.text_input("Search by name or phone")

if search:
    result = df[df["Name"].str.contains(search, case=False, na=False) |
                df["Phone"].str.contains(search, na=False)]
    st.dataframe(result)
