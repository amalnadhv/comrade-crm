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

    # ---------------- CSS (BUTTON DESIGN) ----------------
    st.markdown("""
    <style>
    /* 1. Base Button Styling (Midnight Indigo Theme) */
        div.stButton > button {
            width: 100%;
            height: 50px;
            border-radius: 12px;
            font-weight: 600;
            /* A rich, deep Indigo that isn't black */
            background-color: #1e1b4b; 
            color: #e0e7ff;
            /* Subtle blue border to define the shape */
            border: 1px solid rgba(99, 102, 241, 0.3);
            transition: all 0.3s ease;
        }

        /* 2. Hover Effect (Glow) */
        div.stButton > button:hover {
            background-color: #312e81; /* Lighter Indigo on hover */
            border: 1px solid #818cf8;
            box-shadow: 0 0 15px rgba(79, 70, 229, 0.4);
            transform: scale(1.02);
        }

        /* 3. The Active/Primary Button (Vibrant Gradient) */
        div.stButton > button[kind="primary"] {
            border: none;
            /* Vibrant Indigo to Purple Gradient */
            background: linear-gradient(135deg, #4f46e5, #9333ea) !important;
            color: white !important;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.5);
        }
        
        /* 4. Sidebar spacing */
        section[data-testid="stSidebar"] div.stButton {
            margin-bottom: 10px;
        }
    
    </style>
    """, unsafe_allow_html=True)

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("📊 Comrade CRM")
    st.sidebar.write(f"👤 {st.session_state.user['username']}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()

    # ---------------- MENU (LEADS ABOVE CUSTOMERS) ----------------
    menu = {
        "Dashboard": dashboard_page,
        "Leads": leads_page,
        "Customers": customers_page,
        "Follow-ups": followups_page,
        "Quotations": quotations_page,
        "Reports": reports_page,
        "Settings": settings_page
    }

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📌 Navigation")

    # ---------------- BUTTON NAVIGATION ----------------
    colors = {
        "Dashboard": "#4CAF50",
        "Leads": "#2196F3",
        "Customers": "#FF9800",
        "Follow-ups": "#9C27B0",
        "Quotations": "#00BCD4",
        "Reports": "#607D8B",
        "Settings": "#F44336"
    }

    for label in menu.keys():
        if st.sidebar.button(f"⬤ {label}", key=label):
            st.session_state.page = label
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
