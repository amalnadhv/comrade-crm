import streamlit as st

from database import init_db, validate_user

from pages.dashboard import dashboard_page
from pages.customers import customers_page
from pages.leads import leads_page
from pages.followups import followups_page
from pages.quotations import quotations_page
from pages.reports import reports_page
from pages.settings import settings_page


st.set_page_config(page_title="Comrade CRM", layout="wide")
init_db()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ---------------- LOGIN ----------------
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = validate_user(username, password)

        if user:
            st.session_state.user = {
                "id": user[0],
                "username": user[1],
                "role": user[2]
            }

            st.session_state.page = "Dashboard"
            st.rerun()

        else:
            st.error("Invalid credentials")


# ---------------- APP ----------------
def app():

    st.sidebar.title("📊 Comrade CRM")
    st.sidebar.write(f"👤 {st.session_state.user['username']}")

    # logout
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.page = "Dashboard"
        st.rerun()

  # ---------------- MENU ----------------
menu = {
    "Dashboard": dashboard_page,
    "Customers": customers_page,
    "Leads": leads_page,
    "Follow-ups": followups_page,
    "Quotations": quotations_page,
    "Reports": reports_page,
    "Settings": settings_page
}

# ensure valid page
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if st.session_state.page not in menu:
    st.session_state.page = "Dashboard"


# ---------------- SIDEBAR (PRO UI) ----------------
st.sidebar.title("📊 Comrade CRM")
st.sidebar.write(f"👤 {st.session_state.user['username']}")

if st.sidebar.button("🏠 Dashboard"):
    st.session_state.page = "Dashboard"
    st.rerun()

if st.sidebar.button("👥 Customers"):
    st.session_state.page = "Customers"
    st.rerun()

if st.sidebar.button("🧾 Leads"):
    st.session_state.page = "Leads"
    st.rerun()

if st.sidebar.button("📞 Follow-ups"):
    st.session_state.page = "Follow-ups"
    st.rerun()

if st.sidebar.button("📑 Quotations"):
    st.session_state.page = "Quotations"
    st.rerun()

if st.sidebar.button("📊 Reports"):
    st.session_state.page = "Reports"
    st.rerun()

if st.sidebar.button("⚙️ Settings"):
    st.session_state.page = "Settings"
    st.rerun()

st.sidebar.markdown("---")

# ---------------- PAGE RENDER ----------------
menu[st.session_state.page]()
# ---------------- ENTRY POINT ----------------
if st.session_state.user is None:
    login()
else:
    app()
