import streamlit as st
from database import create_user, get_user

# ---------------- LOGIN / SIGNUP ----------------
def auth_page():
    st.sidebar.title("🔐 Account")

    tab1, tab2 = st.sidebar.tabs(["Login", "Signup"])

    # ---------------- LOGIN ----------------
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            user = get_user(username)

            if user and user[2] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = user[1]
                st.session_state["status"] = user[3]  # subscription status
                st.success("Login successful")
            else:
                st.error("Invalid username or password")

    # ---------------- SIGNUP ----------------
    with tab2:
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")

        if st.button("Create Account"):
            try:
                create_user(new_user, new_pass)
                st.success("Account created! Please login.")
            except:
                st.error("Username already exists")


# ---------------- SESSION HELPERS ----------------
def is_logged_in():
    return st.session_state.get("logged_in", False)


def logout():
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()


def is_active():
    return st.session_state.get("status") == "active"
