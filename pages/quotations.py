import streamlit as st
import pandas as pd
from datetime import date

from database import add_quotation, get_quotations, get_customers


def quotations_page():

    st.title("💼 Quotations")

    df = get_quotations()
    if df is None:
        df = pd.DataFrame()

    # ---------------- CUSTOMERS ----------------
    customers = get_customers()

    if customers is None:
        customers = pd.DataFrame()
    else:
        customers = pd.DataFrame(
            customers,
            columns=["id", "name", "phone", "email", "company", "status"]
        )

    customer_map = {}

    if not customers.empty:
        for row in customers.itertuples():
            customer_map[row.id] = f"{row.name} ({row.company})"

    # ---------------- ADD QUOTATION ----------------
    with st.expander("➕ Create Quotation"):

        if not customer_map:
            st.warning("No customers found")
            return

        customer_id = st.selectbox(
            "Select Customer",
            list(customer_map.keys()),
            format_func=lambda x: customer_map[x]
        )

        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input("Amount", min_value=0.0, step=100.0)
            discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, step=1.0)

        with col2:
            tax = st.number_input("Tax (%)", min_value=0.0, max_value=100.0, step=1.0)
            status = st.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

        # ---------------- VERSION LOGIC ----------------
        existing_versions = df[df["customer_name"] == customer_map.get(customer_id, "")]

        next_version = f"V{len(existing_versions) + 1}"

        st.info(f"📌 Version: {next_version}")

        # ---------------- CALCULATION ----------------
        discounted_amount = amount - (amount * discount / 100)
        total = discounted_amount + (discounted_amount * tax / 100)

        st.success(f"💰 Total: {total:.2f}")

        if st.button("Save Quotation"):

            customer_name = customer_map[customer_id]

            add_quotation(
                customer_name,
                amount,
                discount,
                tax,
                total,
                status,
                str(date.today()),
                next_version
            )

            st.success("Quotation saved!")
            st.rerun()

    st.markdown("---")

    # ---------------- LIST ----------------
    st.subheader("All Quotations")

    if df.empty:
        st.info("No quotations found")
        return

    st.dataframe(df, use_container_width=True)
