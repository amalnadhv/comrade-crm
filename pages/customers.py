import streamlit as st
import pandas as pd
import time

from database import (
    add_customer,
    get_customers,
    update_customer,
    delete_customer
)



# =====================================================
# LOAD DATA
# =====================================================

def load_df():

    rows = get_customers()

    return pd.DataFrame(
        rows,
        columns=[
            "id",
            "name",
            "phone",
            "email",
            "company",
            "status"
        ]
    )



# =====================================================
# MESSAGE SYSTEM
# =====================================================

def show_message(msg):

    st.session_state["msg"] = msg
    st.session_state["msg_time"] = time.time()



def render_message():

    if st.session_state.get("msg"):

        st.success(
            st.session_state["msg"]
        )

        if time.time() - st.session_state["msg_time"] > 3:

            st.session_state["msg"] = None
            st.session_state["msg_time"] = None



# =====================================================
# CLEAR FORM
# =====================================================

def clear_customer_form():

    for key in [
        "cust_name",
        "cust_phone",
        "cust_email",
        "cust_company",
        "cust_status"
    ]:

        st.session_state.pop(
            key,
            None
        )



# =====================================================
# CUSTOMER PAGE
# =====================================================

def customers_page():


    role = st.session_state.user["role"]



    # =================================================
    # SESSION CONTROL (SAVE PROTECTION)
    # =================================================


    if "customer_saved" not in st.session_state:

        st.session_state.customer_saved = True



    if "edit_customer_id" not in st.session_state:

        st.session_state.edit_customer_id = None



    # =================================================
    # CSS STYLE
    # =================================================


    st.markdown(
    """
    <style>


    .crm-header {

        background:
        linear-gradient(
            135deg,
            #11998e,
            #38ef7d
        );

        padding:22px 30px;

        border-radius:15px;

        margin-bottom:15px;

        box-shadow:
        0 4px 12px rgba(0,0,0,.15);

    }



    .crm-title {

        color:white;

        font-size:32px;

        font-weight:800;

    }



    .crm-subtitle {

        color:#eaffea;

        font-size:15px;

        margin-top:5px;

    }



    .table-header {

        background:
        linear-gradient(
            135deg,
            #11998e,
            #38ef7d
        );

        color:white;

        padding:8px;

        border-radius:8px;

        text-align:center;

        font-weight:bold;

    }



    .status-new {

        color:#2196f3;

        font-weight:bold;

    }


    .status-contact {

        color:#ff9800;

        font-weight:bold;

    }


    .status-won {

        color:#28a745;

        font-weight:bold;

    }


    .status-lost {

        color:#dc3545;

        font-weight:bold;

    }



    div.stButton > button {

        border-radius:10px;

        height:36px;

        font-weight:bold;

    }


    </style>

    """,

    unsafe_allow_html=True
    )



    # =================================================
    # HEADER
    # =================================================


    st.markdown(
    """

    <div class="crm-header">

        <div class="crm-title">
            👥 Customers Dashboard
        </div>

        <div class="crm-subtitle">
            Manage customers, relationships and business growth
        </div>

    </div>

    """,

    unsafe_allow_html=True
    )



    render_message()



    df = load_df()



    # =================================================
    # SUMMARY
    # =================================================


    total = len(df)


    new = len(
        df[df.status=="New"]
    ) if not df.empty else 0



    contacted = len(
        df[df.status=="Contacted"]
    ) if not df.empty else 0



    won = len(
        df[df.status=="Won"]
    ) if not df.empty else 0



    lost = len(
        df[df.status=="Lost"]
    ) if not df.empty else 0



    c1,c2,c3,c4,c5 = st.columns(5)



    c1.metric(
        "👥 Total",
        total
    )


    c2.metric(
        "🔵 New",
        new
    )


    c3.metric(
        "🟠 Contacted",
        contacted
    )


    c4.metric(
        "🟢 Won",
        won
    )


    c5.metric(
        "🔴 Lost",
        lost
    )



    st.markdown(
    """
    <hr style="
    margin:5px 0;
    border:0;
    border-top:1px solid #ddd;
    ">
    """,

    unsafe_allow_html=True
    )



    # =================================================
    # NEW CUSTOMER BUTTON
    # =================================================


    if st.button(
        "➕ New Customer",
        width="stretch"
    ):


        st.session_state.customer_saved = False

        st.session_state.edit_customer_id = None



    # =================================================
    # ADD CUSTOMER FORM
    # =================================================


    if not st.session_state.customer_saved:


        with st.container(border=True):


            st.subheader(
                "➕ Add New Customer"
            )


            col1,col2 = st.columns(2)



            with col1:


                name = st.text_input(
                    "Contact Name",
                    key="cust_name"
                )


                phone = st.text_input(
                    "Phone",
                    key="cust_phone"
                )


                email = st.text_input(
                    "Email",
                    key="cust_email"
                )



            with col2:


                company = st.text_input(
                    "Company",
                    key="cust_company"
                )


                status = st.selectbox(
                    "Status",
                    [
                        "New",
                        "Contacted",
                        "Won",
                        "Lost"
                    ],
                    key="cust_status"
                )



            save = st.button(
                "💾 Save Customer",
                width="stretch"
            )



            if save:


                if not name or not phone:


                    st.error(
                        "Name and Phone are required"
                    )


                else:


                    add_customer(
                        name,
                        phone,
                        email,
                        company,
                        status
                    )


                    st.session_state.customer_saved=True


                    clear_customer_form()


                    show_message(
                        "Customer saved successfully ✅"
                    )


                    st.rerun()
                        # =================================================
    # EDIT CUSTOMER
    # =================================================


    if st.session_state.edit_customer_id:


        edit_id = st.session_state.edit_customer_id


        edit_data = df[
            df.id == edit_id
        ]


        if not edit_data.empty:


            row = edit_data.iloc[0]


            st.markdown("---")


            with st.container(border=True):


                st.subheader(
                    f"✏️ Edit Customer : {row['name']}"
                )


                col1,col2 = st.columns(2)



                with col1:


                    edit_name = st.text_input(
                        "Contact Name",
                        value=row["name"],
                        key=f"edit_name_{edit_id}"
                    )


                    edit_phone = st.text_input(
                        "Phone",
                        value=row["phone"],
                        key=f"edit_phone_{edit_id}"
                    )


                    edit_email = st.text_input(
                        "Email",
                        value=row["email"],
                        key=f"edit_email_{edit_id}"
                    )



                with col2:


                    edit_company = st.text_input(
                        "Company",
                        value=row["company"],
                        key=f"edit_company_{edit_id}"
                    )



                    status_list = [
                        "New",
                        "Contacted",
                        "Won",
                        "Lost"
                    ]



                    current_status = row["status"]



                    if current_status not in status_list:

                        current_status="New"



                    edit_status = st.selectbox(
                        "Status",
                        status_list,
                        index=status_list.index(
                            current_status
                        ),
                        key=f"edit_status_{edit_id}"
                    )



                c1,c2 = st.columns(2)



                with c1:


                    if st.button(
                        "💾 Update Customer",
                        key=f"update_customer_{edit_id}",
                        width="stretch"
                    ):


                        update_customer(
                            edit_id,
                            edit_name,
                            edit_phone,
                            edit_email,
                            edit_company,
                            edit_status
                        )



                        st.session_state.edit_customer_id=None


                        show_message(
                            "Customer updated successfully ✅"
                        )


                        st.rerun()



                with c2:


                    if st.button(
                        "❌ Cancel",
                        key=f"cancel_customer_{edit_id}",
                        width="stretch"
                    ):


                        st.session_state.edit_customer_id=None


                        st.rerun()



    # =================================================
    # SEARCH
    # =================================================


    st.markdown("---")


    search = st.text_input(
        "🔍 Search Customers"
    )



    if search:


        df = df[
            df.astype(str)
            .apply(
                lambda x:
                x.str.contains(
                    search,
                    case=False,
                    na=False
                )
            )
            .any(axis=1)
        ]



    # =================================================
    # EXPORT
    # =================================================


    st.markdown(
        "### 📤 Export Customers"
    )



    csv = df.to_csv(
        index=False
    ).encode("utf-8")



    st.download_button(
        "⬇ Download Customers CSV",
        csv,
        "customers.csv",
        "text/csv",
        width="stretch"
    )



    st.markdown("---")



    # =================================================
    # CUSTOMER LIST TITLE
    # =================================================


    st.subheader(
        "👥 Customer List"
    )



    if df.empty:


        st.info(
            "No customers found"
        )


        return
            # =================================================
    # TABLE HEADER
    # =================================================


    headers = st.columns(
        [
            2.2,
            2,
            1.5,
            2.2,
            1.3,
            1.5
        ]
    )


    titles = [

        "🏢 Company",

        "👤 Contact",

        "📞 Phone",

        "✉ Email",

        "🏷 Status",

        "⚙ Actions"

    ]


    for col,title in zip(headers,titles):

        col.markdown(
        f"""
        <div class="table-header">
            {title}
        </div>
        """,
        unsafe_allow_html=True
        )



    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )



    # =================================================
    # CUSTOMER ROWS
    # =================================================


    for row in df.itertuples():



        cols = st.columns(
            [
                2.2,
                2,
                1.5,
                2.2,
                1.3,
                1.5
            ]
        )



        with cols[0]:

            st.write(
                f"🏢 {row.company}"
            )



        with cols[1]:

            st.write(
                row.name
            )



        with cols[2]:

            st.write(
                row.phone
            )



        with cols[3]:

            st.write(
                row.email
            )



        with cols[4]:


            if row.status == "New":


                st.markdown(
                """
                <span class="status-new">
                🔵 New
                </span>
                """,
                unsafe_allow_html=True
                )



            elif row.status == "Contacted":


                st.markdown(
                """
                <span class="status-contact">
                🟠 Contacted
                </span>
                """,
                unsafe_allow_html=True
                )



            elif row.status == "Won":


                st.markdown(
                """
                <span class="status-won">
                🟢 Won
                </span>
                """,
                unsafe_allow_html=True
                )



            else:


                st.markdown(
                """
                <span class="status-lost">
                🔴 Lost
                </span>
                """,
                unsafe_allow_html=True
                )



        with cols[5]:


            b1,b2 = st.columns(2)



            with b1:


                if st.button(
                    "✏️",
                    key=f"edit_customer_{row.id}",
                    help="Edit Customer"
                ):


                    st.session_state.edit_customer_id = row.id

                    st.rerun()



            with b2:


                if role == "Admin":


                    if st.button(
                        "🗑️",
                        key=f"delete_customer_{row.id}",
                        help="Delete Customer"
                    ):


                        delete_customer(
                            row.id
                        )


                        show_message(
                            "Customer deleted 🗑️"
                        )


                        st.rerun()



        # row separator

        st.markdown(
        """
        <hr style="
        margin:4px 0px;
        border:0;
        border-top:1px solid #eeeeee;
        ">
        """,
        unsafe_allow_html=True
        )
        
