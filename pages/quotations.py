import streamlit as st
import pandas as pd
from datetime import date

from database import add_quotation, get_quotations
from utils.emailer import send_email

send_email(
    "client@email.com",
    "Quotation from Comrade CRM",
    "Please find attached your quotation."
)

def quotations_page():

    st.title("💼 Quotations")

    df = get_quotations()

    if df is None or df.empty:
        df = pd.DataFrame(columns=[
            "id", "customer_name", "amount", "discount",
            "tax", "total", "status", "created_on"
        ])

    # ---------------- ADD QUOTATION ----------------
    with st.expander("➕ Create Quotation"):

        col1, col2 = st.columns(2)

        with col1:
            customer_name = st.text_input("Customer Name")
            amount = st.number_input("Amount", min_value=0.0, step=100.0)
            discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, step=1.0)

        with col2:
            tax = st.number_input("Tax (%)", min_value=0.0, max_value=100.0, step=1.0)
            status = st.selectbox("Status", ["Draft", "Sent", "Approved", "Rejected"])

        # ---------------- CALCULATION ----------------
        discounted_amount = amount - (amount * discount / 100)
        total = discounted_amount + (discounted_amount * tax / 100)

        st.info(f"💰 Total Amount: {total:.2f}")

        if st.button("Save Quotation"):
            if customer_name:
                add_quotation(
                    customer_name,
                    amount,
                    discount,
                    tax,
                    total,
                    status,
                    str(date.today())
                )
                st.success("Quotation saved!")
                st.rerun()
            else:
                st.error("Customer name required")

    st.markdown("---")

    from utils.pdf_generator import generate_quotation_pdf
    
    data = {
        "Customer": customer_name,
        "Amount": amount,
        "Discount": discount,
        "Tax": tax,
        "Total": total,
        "Status": status
    }
    
    filename = f"quotation_{customer_name}.pdf"
    generate_quotation_pdf(filename, data)
    
    with open(filename, "rb") as f:
        st.download_button(
            "⬇ Download PDF",
            f,
            file_name=filename
        )
    
    # ---------------- LIST ----------------
    st.subheader("All Quotations")

    if df.empty:
        st.info("No quotations found")
        return

    st.dataframe(df, use_container_width=True)
