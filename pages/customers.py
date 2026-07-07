import streamlit as st
import pandas as pd
import time

from database import (
    add_customer,
    get_customers,
    update_customer,
    delete_customer
)


# ---------------- LOAD DATA ----------------

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


# ---------------- MESSAGE SYSTEM ----------------

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
            st.rerun()



# ---------------- RESET FORM ----------------

def reset_add_form():

    keys = [
        "add_name",
        "add_phone",
        "add_email",
        "add_company",
        "add_status"
    ]

    for k in keys:
        st.session_state.pop(k, None)



# ---------------- PAGE ----------------

def customers_page():

    role = st.session_state.user["role"]


    # ---------------- STYLE ----------------

    st.markdown(
    """
    <style>

    .crm-header {

        background:linear-gradient(
            135deg,
            #11998e,
            #38ef7d
        );

        padding:22px 30px;

        border-radius:15px;

        margin-bottom:20px;

        box-shadow:0 4px 12px rgba(0,0,0,.15);

    }


    .crm-title {

        color:white;

        font-size:32px;

        font-weight:800;

    }


    .crm-subtitle {

        color:#eaffea;

        font-size:15px;

    }


    .table-head {

        background:#11998e;

        color:white;

        padding:10px;

        border-radius:8px;

        text-align:center;

        font-weight:bold;

    }


    div.stButton > button {

        border-radius:10px;

        height:35px;

        font-weight:bold;

    }


    </style>
    """,
    unsafe_allow_html=True
    )



    # ---------------- HEADER ----------------


    st.markdown(
    """
    <div class="crm-header">

        <div class="crm-title">
            👥 Customers Dashboard
        </div>

        <div class="crm-subtitle">
            Manage customer relationships efficiently
        </div>

    </div>
    """,
    unsafe_allow_html=True
    )



    render_message()


    df = load_df()



    # ---------------- SUMMARY ----------------


    total = len(df)

    new = len(df[df.status=="New"])
    contacted = len(df[df.status=="Contacted"])
    won = len(df[df.status=="Won"])
    lost = len(df[df.status=="Lost"])



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



    st.markdown("---")



    # ---------------- ADD CUSTOMER ----------------


    with st.expander(
        "➕ Add New Customer"
    ):


        col1,col2 = st.columns(2)


        with col1:

            name = st.text_input(
                "Contact Name",
                key="add_name"
            )


            phone = st.text_input(
                "Phone",
                key="add_phone"
            )


            email = st.text_input(
                "Email",
                key="add_email"
            )



        with col2:

            company = st.text_input(
                "Company",
                key="add_company"
            )


            status = st.selectbox(
                "Status",
                [
                    "New",
                    "Contacted",
                    "Won",
                    "Lost"
                ],
                key="add_status"
            )



        if st.button(
            "💾 Save Customer",
            key="save_customer"
        ):


            if name and phone:


                add_customer(
                    name,
                    phone,
                    email,
                    company,
                    status
                )


                reset_add_form()


                show_message(
                    "Customer added successfully ✅"
                )


                st.rerun()



            else:


                show_message(
                    "Name and Phone are required ❌"
                )

                st.rerun()



    st.markdown("---")



    # ---------------- SEARCH ----------------


    search = st.text_input(
        "🔍 Search customers"
    )



    if search:


        df = df[
            df.astype(str)
            .apply(
                lambda x:
                x.str.contains(
                    search,
                    case=False
                )
            )
            .any(axis=1)
        ]



    # ---------------- EDIT ----------------


    if "edit_id" not in st.session_state:

        st.session_state.edit_id=None



    if st.session_state.edit_id:


        edit_id = st.session_state.edit_id


        row = df[
            df.id==edit_id
        ]


        if not row.empty:


            row=row.iloc[0]


            st.subheader(
                f"✏ Edit Customer : {row['name']}"
            )


            n = st.text_input(
                "Name",
                row["name"]
            )

            p = st.text_input(
                "Phone",
                row["phone"]
            )

            e = st.text_input(
                "Email",
                row["email"]
            )

            c = st.text_input(
                "Company",
                row["company"]
            )


            s = st.selectbox(
                "Status",
                [
                    "New",
                    "Contacted",
                    "Won",
                    "Lost"
                ]
            )



            if st.button(
                "💾 Update Customer"
            ):


                update_customer(
                    edit_id,
                    n,
                    p,
                    e,
                    c,
                    s
                )


                st.session_state.edit_id=None


                show_message(
                    "Customer updated successfully ✅"
                )


                st.rerun()



    st.markdown("---")



    # ---------------- EXPORT ----------------


    csv = df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        "⬇ Download Customers CSV",
        csv,
        "customers.csv",
        "text/csv"
    )



    st.markdown("---")



    # ---------------- CUSTOMER TABLE ----------------


    st.subheader(
        "👥 Customer List"
    )


    if df.empty:

        st.info(
            "No customers found"
        )

        return



    headers = st.columns(
        [
            2,
            2,
            1.5,
            2,
            1.2,
            1.2
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



    for c,t in zip(headers,titles):

        c.markdown(
        f"""
        <div class="table-head">
        {t}
        </div>
        """,
        unsafe_allow_html=True
        )



    # ---------------- ROWS ----------------


    for row in df.itertuples():


        cols = st.columns(
            [
                2,
                2,
                1.5,
                2,
                1.2,
                1.2
            ]
        )


        cols[0].write(
            f"🏢 {row.company}"
        )


        cols[1].write(
            row.name
        )


        cols[2].write(
            row.phone
        )


        cols[3].write(
            row.email
        )


        if row.status=="New":

            cols[4].markdown(
                "🔵 New"
            )

        elif row.status=="Contacted":

            cols[4].markdown(
                "🟠 Contacted"
            )

        elif row.status=="Won":

            cols[4].markdown(
                "🟢 Won"
            )

        else:

            cols[4].markdown(
                "🔴 Lost"
            )



        with cols[5]:

            b1,b2 = st.columns(2)


            with b1:

                if st.button(
                    "✏",
                    key=f"edit_{row.id}",
                    help="Edit Customer"
                ):

                    st.session_state.edit_id=row.id
                    st.rerun()



            with b2:

                if role=="Admin":

                    if st.button(
                        "🗑",
                        key=f"delete_{row.id}",
                        help="Delete Customer"
                    ):

                        delete_customer(
                            row.id
                        )


                        show_message(
                            "Customer deleted 🗑"
                        )


                        st.rerun()



        st.markdown(
        """
        <hr style="
        margin:4px 0;
        border:0;
        border-top:1px solid #eeeeee;
        ">
        """,
        unsafe_allow_html=True
        )
