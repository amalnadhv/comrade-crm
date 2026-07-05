import streamlit as st

from database import init_db, validate_user

from pages.dashboard import dashboard_page
from pages.leads import leads_page
from pages.customers import customers_page
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

    st.title("🔐 Comrade CRM Login")

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

    # ---------------- CSS FOR BUTTON STYLE ----------------
    st.markdown("""
    <style>

    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 12px;
        font-weight: 600;
        text-align: left;
        padding-left: 12px;
        border: none;
        transition: 0.2s;
        color: white;
    }

    section[data-testid="stSidebar"] div.stButton > button:hover {
        transform: scale(1.03);
        opacity: 0.9;
    }

    section[data-testid="stSidebar"] div.stButton {
        margin-bottom: 6px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- SIDEBAR HEADER ----------------
    st.sidebar.title("📊 Comrade CRM")
    st.sidebar.write(f"👤 {st.session_state.user['username']}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()

    # ---------------- MENU (LEADS FIRST) ----------------
    menu = [
        ("🏠 Dashboard", "Dashboard", "#4CAF50"),
        ("🎯 Leads", "Leads", "#2196F3"),
        ("👥 Customers", "Customers", "#FF9800"),
        ("📞 Follow-ups", "Follow-ups", "#9C27B0"),
        ("📑 Quotations", "Quotations", "#00BCD4"),
        ("📊 Reports", "Reports", "#607D8B"),
        ("⚙️ Settings", "Settings", "#F44336")
    ]

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📌 Navigation")

    # ---------------- NAV BUTTONS ----------------
    for label, page, color in menu:

        if st.sidebar.button(label, key=page):

            st.session_state.page = page
            st.rerun()

    st.sidebar.markdown("---")

    # ---------------- PAGE ROUTING ----------------
    if st.session_state.page == "Dashboard":
        dashboard_page()

    elif st.session_state.page == "Leads":
        leads_page()

    elif st.session_state.page == "Customers":
        customers_page()

    elif st.session_state.page == "Follow-ups":
        followups_page()

    elif st.session_state.page == "Quotations":
        quotations_page()

    elif st.session_state.page == "Reports":
        reports_page()

    elif st.session_state.page == "Settings":
        settings_page()


# ---------------- ENTRY POINT ----------------
def main():

    if st.session_state.user is None:
        login()
        st.stop()

    app()


main()
