import streamlit as st

from database import init_db, validate_user

from pages.dashboard import dashboard_page
from pages.customers import customers_page
from pages.leads import leads_page
from pages.followups import followups_page
from pages.quotations import quotations_page
from pages.reports import reports_page


# ---------------- INIT ----------------
st.set_page_config(page_title="Comrade CRM", layout="wide")
init_db()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None


def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------- LOGIN PAGE ----------------
def login():

    st.title("🔐 Comrade CRM Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = validate_user(username, password)

        if user:
            st.session_state.user = {
                "id": user[0],
                "username": user[1],
                "role": user[3]
            }
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")


# ---------------- APP ----------------
def app():

    st.sidebar.title("Comrade CRM")

    st.sidebar.write(f"👤 {st.session_state.user['username']}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    if role == "Admin":
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "Customers", "Leads", "Follow-ups", "Quotations", "Reports", "Settings"]
        )
    else:
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "Customers", "Leads", "Follow-ups"]
        )

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Customers", "Leads", "Follow-ups", "Quotations", "Reports"]
    )

   st.sidebar.markdown("""
    # 💼 Comrade CRM
    
    ### Sales & Lead Management
    ---
    """)

    st.session_state.user = {
        "id": user[0],
        "username": user[1],
        "role": user[2]
    }

    st.sidebar.markdown(f"""
    👤 Logged in as:  
    **{st.session_state.user['username']}**
    
    Role: `{st.session_state.user['role']}`
    """)

    if page == "Dashboard":
        dashboard_page()
    elif page == "Customers":
        customers_page()
    elif page == "Leads":
        leads_page()
    elif page == "Follow-ups":
        followups_page()
    elif page == "Quotations":
        quotations_page()
    elif page == "Reports":
        reports_page()


# ---------------- ROUTER ----------------
if st.session_state.user is None:
    login()
else:
    app()
