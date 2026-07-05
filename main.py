import streamlit as st

from database import init_db
from pages.dashboard import dashboard_page
from pages.customers import customers_page
from pages.leads import leads_page
from pages.followups import followups_page
from pages.reports import reports_page
from pages.settings import settings_page

# ---------------- APP CONFIG ----------------
st.set_page_config(
    page_title="Comrade CRM",
    page_icon="💼",
    layout="wide"
)

# ---------------- DATABASE ----------------
init_db()

# ---------------- SIDEBAR ----------------
st.sidebar.image(
    "https://img.icons8.com/color/96/business.png",
    width=70
)

st.sidebar.title("Comrade CRM")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Customers",
        "Leads",
        "Follow Ups",
        "Reports",
        "Settings"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Version 2.0")

# ---------------- PAGE ROUTER ----------------
if page == "Dashboard":
    dashboard_page()

elif page == "Customers":
    customers_page()

elif page == "Leads":
    leads_page()

elif page == "Follow Ups":
    followups_page()

elif page == "Reports":
    reports_page()

elif page == "Settings":
    settings_page()
