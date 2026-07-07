import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import date

from database import (
    add_quotation,
    get_quotations,
    get_customers
)

from utils.pdf_generator import generate_quotation_pdf


DB_NAME = "crm.db"



# =====================================================
# UPDATE
# =====================================================

def update_quotation(
    qid,
    customer_name,
    items,
    subtotal,
    discount,
    tax,
    total,
    status,
    version
):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()


    cur.execute(
        """
        UPDATE quotations
        SET
            customer_name=?,
            items=?,
            subtotal=?,
            discount=?,
            tax=?,
            total=?,
            status=?,
            version=?
        WHERE id=?
        """,
        (
            customer_name,
            json.dumps(items),
            subtotal,
            discount,
            tax,
            total,
            status,
            version,
            qid
        )
    )


    conn.commit()
    conn.close()



# =====================================================
# DELETE
# =====================================================

def delete_quotation(qid):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()


    cur.execute(
        "DELETE FROM quotations WHERE id=?",
        (qid,)
    )


    conn.commit()
    conn.close()



# =====================================================
# RESET
# =====================================================

def reset_quote():

    for key in [
        "quote_items",
        "edit_id",
        "edit_loaded",
        "edit_customer",
        "edit_status"
    ]:

        if key in st.session_state:

            del st.session_state[key]
def quotations_page():


    # ===============================
    # STYLE
    # ===============================

    st.markdown(
        """
        <style>

        .header {

            background:
            linear-gradient(
            135deg,
            #ffffff,
            #f1f5f9
            );

            padding:25px;

            border-radius:16px;

            border:1px solid #e2e8f0;

            margin-bottom:20px;

        }


        .stat-card {

            background:white;

            padding:15px;

            border-radius:14px;

            border:1px solid #e5e7eb;

            text-align:center;

        }


        .stat-number {

            font-size:26px;

            font-weight:bold;

        }
            
            
                    .table-row {
            
                        padding:8px;
            
                        border-bottom:1px solid #e5e7eb;
            
                    }
            
            
                    </style>
            
                    """,
            
                    unsafe_allow_html=True
                )



    # ===============================
    # SESSION
    # ===============================


    if "quote_items" not in st.session_state:

        st.session_state.quote_items=[]


    if "edit_id" not in st.session_state:

        st.session_state.edit_id=None


    if "edit_loaded" not in st.session_state:

        st.session_state.edit_loaded=False


    if "edit_customer" not in st.session_state:

        st.session_state.edit_customer=None


    if "edit_status" not in st.session_state:

        st.session_state.edit_status="Draft"



    # ===============================
    # HEADER
    # ===============================


    st.markdown(
        """
        <div class="header">

        <h1>
        💼 Quotations
        </h1>

        Manage customer quotations

        </div>

        """,

        unsafe_allow_html=True
    )
        # =====================================================
    # LOAD CUSTOMERS
    # =====================================================


    customers = get_customers()


    customers = pd.DataFrame(
        customers,
        columns=[
            "id",
            "name",
            "phone",
            "email",
            "company",
            "status"
        ]
    )


    customer_map = {

        row.id:
        f"{row.name} - {row.company}"

        for row in customers.itertuples()

    }


    customer_options = list(
        customer_map.keys()
    )



    if not customer_options:

        st.warning(
            "Please add customers first"
        )

        return



    # =====================================================
    # SUMMARY CARDS
    # =====================================================


    quotes = get_quotations()


    if isinstance(quotes,list):

        quote_count=len(quotes)

    else:

        quote_count=len(quotes)



    s1,s2,s3 = st.columns(3)


    with s1:

        st.markdown(
            f"""
            <div class="stat-card">

            Total Quotes

            <div class="stat-number">

            {quote_count}

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )



    with s2:

        st.markdown(
            """
            <div class="stat-card">

            Status

            <div class="stat-number">

            CRM

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )



    with s3:

        st.markdown(
            """
            <div class="stat-card">

            Version

            <div class="stat-number">

            V1

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )



    st.divider()



    # =====================================================
    # NEW QUOTATION BUTTON
    # =====================================================


    if st.button(
        "➕ New Quotation",
        width="content"
    ):

        reset_quote()

        st.session_state.quote_items=[]

        st.rerun()



    # =====================================================
    # FORM
    # =====================================================


    st.subheader(
        "Create Quotation"
    )



    c1,c2 = st.columns(2)



    with c1:


        customer_id = st.selectbox(

            "Customer",

            customer_options,

            format_func=lambda x:
            customer_map[x],

            key="customer_select"

        )



    with c2:


        status = st.selectbox(

            "Status",

            [
                "Draft",
                "Sent",
                "Approved",
                "Rejected"
            ],

            key="status_select"

        )



    st.divider()



    # =====================================================
    # ITEMS
    # =====================================================


    st.subheader(
        "Items"
    )



    i1,i2,i3,i4 = st.columns(
        [4,1,2,1]
    )



    with i1:

        item = st.text_input(
            "Description",
            key="item_input"
        )



    with i2:

        qty = st.number_input(
            "Qty",
            min_value=1.0,
            value=1.0,
            key="qty_input"
        )



    with i3:

        price = st.number_input(
            "Price",
            min_value=0.0,
            value=0.0,
            key="price_input"
        )



    with i4:

        st.write("")

        add_item = st.button(
            "➕",
            width="content"
        )



    if add_item:


        if item.strip():


            st.session_state.quote_items.append(

                {
                    "item":item,
                    "qty":qty,
                    "price":price
                }

            )

            st.rerun()


        else:

            st.warning(
                "Enter item name"
            )



    subtotal=0



    if st.session_state.quote_items:


        for index,item_row in enumerate(
            st.session_state.quote_items
        ):


            a,b,c,d = st.columns(
                [4,1,2,1]
            )


            a.write(
                item_row["item"]
            )


            b.write(
                item_row["qty"]
            )


            c.write(
                item_row["price"]
            )



            if d.button(
                "❌",
                key=f"remove_{index}"
            ):

                st.session_state.quote_items.pop(
                    index
                )

                st.rerun()



            subtotal += (
                item_row["qty"]
                *
                item_row["price"]
            )



    else:


        st.info(
            "No items added"
        )



    st.divider()



    # =====================================================
    # TOTALS
    # =====================================================


    t1,t2 = st.columns(2)



    with t1:


        discount = st.number_input(
            "Discount %",
            min_value=0.0,
            value=0.0,
            key="discount"
        )


        tax = st.number_input(
            "Tax %",
            min_value=0.0,
            value=0.0,
            key="tax"
        )



    after_discount = (

        subtotal -
        subtotal*discount/100

    )



    total = (

        after_discount +

        after_discount*tax/100

    )



    with t2:


        st.success(
            f"""
            Subtotal : {subtotal:,.2f}

            Total : {total:,.2f}
            """
        )
            # =====================================================
    # SAVE QUOTATION
    # =====================================================


    st.divider()


    if st.button(

        "💾 Save Quotation",

        width="stretch"

    ):



        # Check items

        if not st.session_state.quote_items:


            st.warning(
                "Please add at least one item before saving"
            )

            st.stop()



        customer_name = customer_map[customer_id]



        # ============================
        # EDIT MODE
        # ============================


        if st.session_state.edit_id:



            update_quotation(

                st.session_state.edit_id,

                customer_name,

                st.session_state.quote_items,

                subtotal,

                discount,

                tax,

                total,

                status,

                "V-EDIT"

            )


            st.success(
                "Quotation updated successfully"
            )



        # ============================
        # NEW MODE
        # ============================


        else:



            add_quotation(

                customer_name,

                st.session_state.quote_items,

                subtotal,

                discount,

                tax,

                total,

                status,

                str(date.today()),

                "V1"

            )


            st.success(
                "Quotation saved successfully"
            )



        # clear form

        reset_quote()


        # refresh page

        st.rerun()
            # =====================================================
    # QUOTATION LIST
    # =====================================================


    st.divider()


    st.subheader(
        "📋 Quotation List"
    )



    df = get_quotations()



    # Convert result to dataframe if required

    if isinstance(df, list):

        df = pd.DataFrame(
            df
        )



    if df.empty:


        st.info(
            "No quotations available"
        )



    else:



        # =========================
        # FILTERS
        # =========================


        f1,f2 = st.columns(2)



        with f1:


            search = st.text_input(
                "🔍 Search customer"
            )



        with f2:


            status_filter = st.selectbox(

                "Status",

                [
                    "All",
                    "Draft",
                    "Sent",
                    "Approved",
                    "Rejected"
                ]

            )



        if search:


            df = df[
                df["customer_name"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]



        if status_filter != "All":


            df=df[
                df["status"]
                ==
                status_filter
            ]



        st.markdown(
            """
            <hr>
            """,
            unsafe_allow_html=True
        )



        # HEADER


        h1,h2,h3,h4,h5 = st.columns(
            [
                1.3,
                3.5,
                2,
                1.5,
                2
            ]
        )


        h1.write("**No**")

        h2.write("**Customer**")

        h3.write("**Amount**")

        h4.write("**Status**")

        h5.write("**Action**")



        st.markdown(
            "<hr>",
            unsafe_allow_html=True
        )



        # ROWS


        for _,row in df.iterrows():



            c1,c2,c3,c4,c5 = st.columns(

                [
                    1.3,
                    3.5,
                    2,
                    1.5,
                    2
                ]

            )



            c1.write(
                f"QT-{row['id']:04d}"
            )



            c2.write(
                row["customer_name"]
            )



            c3.write(
                f"{row['total']:,.2f}"
            )



            c4.write(
                row["status"]
            )



            with c5:


                a,b,c = st.columns(3)



                # EDIT

                with a:


                    if st.button(

                        "✏️",

                        key=f"edit_{row['id']}"

                    ):


                        st.session_state.edit_id=row["id"]

                        st.session_state.edit_loaded=False

                        st.rerun()



                # DELETE


                with b:


                    if st.button(

                        "🗑",

                        key=f"delete_{row['id']}"

                    ):


                        delete_quotation(
                            row["id"]
                        )


                        st.success(
                            "Deleted"
                        )


                        st.rerun()



                # PDF


                with c:



                    data=row.to_dict()



                    if isinstance(

                        data.get("items"),

                        str

                    ):


                        try:

                            data["items"]=json.loads(
                                data["items"]
                            )

                        except:

                            data["items"]=[]



                    pdf=generate_quotation_pdf(
                        data
                    )



                    st.download_button(

                        "📄",

                        pdf,

                        file_name=
                        f"quotation_{row['id']}.pdf",

                        mime=
                        "application/pdf",

                        key=
                        f"pdf_{row['id']}"

                    )



            st.markdown(
                "<hr style='margin:2px 0'>",
                unsafe_allow_html=True
            )
            
