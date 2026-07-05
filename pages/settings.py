import streamlit as st
from database import add_user
from utils.backup import backup_db

if st.button("📦 Backup Database"):
    file = backup_db()
    st.success(f"Backup created: {file}")
    
def settings_page():

    st.title("⚙ Settings")

    st.subheader("👤 Create User")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Admin", "Sales"])

    if st.button("Create User"):
        if username and password:
            add_user(username, password, role)
            st.success("User created!")
        else:
            st.error("Fill all fields")

    st.markdown("---")

    st.info("Future: Branding, Email config, API keys")
