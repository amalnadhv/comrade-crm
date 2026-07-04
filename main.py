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
    st.title("👥 Customers Management")

    search = st.text_input("🔎 Search by name or phone")

    filtered = df.copy()

    if search:
        filtered = df[
            filtered["Name"].str.contains(search, case=False, na=False) |
            filtered["Phone"].str.contains(search, na=False)
        ]

    st.write("")

    for i, row in filtered.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,2,2,1])

            col1.write(row["Name"])
            col2.write(row["Phone"])
            col3.write(row["Email"])
            col4.write(row["Company"])
            col5.write(row["Status"])

            # ---------------- DELETE ----------------
            if col6.button("🗑️", key=f"del_{i}"):
                df.drop(i, inplace=True)
                save_data(df)
                st.rerun()

            # ---------------- EDIT EXPANDER ----------------
            with st.expander("✏️ Edit"):
                new_name = st.text_input("Name", row["Name"], key=f"name_{i}")
                new_phone = st.text_input("Phone", row["Phone"], key=f"phone_{i}")
                new_email = st.text_input("Email", row["Email"], key=f"email_{i}")
                new_company = st.text_input("Company", row["Company"], key=f"company_{i}")
                new_status = st.selectbox(
                    "Status",
                    ["New", "Contacted", "Won", "Lost"],
                    index=["New", "Contacted", "Won", "Lost"].index(row["Status"]),
                    key=f"status_{i}"
                )

                if st.button("💾 Save", key=f"save_{i}"):
                    df.at[i, "Name"] = new_name
                    df.at[i, "Phone"] = new_phone
                    df.at[i, "Email"] = new_email
                    df.at[i, "Company"] = new_company
                    df.at[i, "Status"] = new_status

                    save_data(df)
                    st.success("Updated!")
                    st.rerun()

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
