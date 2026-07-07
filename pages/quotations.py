import streamlit as st
import pandas as pd
import json
import sqlite3
from datetime import date

from database import (
    add_quotation,
    get_quotations,
    get_customers
)

from utils.pdf_generator import generate_quotation_pdf


DB_NAME = "crm.db"



# =====================================================
# UPDATE QUOTATION
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
# DELETE QUOTATION
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
# RESET FORM
# =====================================================

def reset_quote():

    st.session_state.quote_items = []

    st.session_state.edit_id = None

    st.session_state.edit_loaded = False

    st.session_state.edit_customer = None

    st.session_state.edit_status = "Draft"


    keys = [

        "item_input",
        "qty_input",
        "price_input",
        "discount",
        "tax",
        "customer_select",
        "status_select"

    ]


    for key in keys:

        if key in st.session_state:

            del st.session_state[key]



# =====================================================
# PAGE
# =====================================================

def quotations_page():



    # ===============================
    # STYLE
    # ===============================

    st.markdown(
        """
        <style>


        .quote-header {

            background:white;

            padding:20px;

            border-radius:15px;

            border:1px solid #e5e7eb;

            margin-bottom:15px;

        }


        .summary-card {

            background:white;

            padding:15px;

            border-radius:12px;

            border:1px solid #e5e7eb;

            text-align:center;

        }


        .summary-number {

            font-size:24px;

            font-weight:bold;

        }


        .quote-row {

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

        st.session_state.quote_items = []


    if "edit_id" not in st.session_state:

        st.session_state.edit_id = None


    if "edit_loaded" not in st.session_state:

        st.session_state.edit_loaded = False


    if "edit_customer" not in st.session_state:

        st.session_state.edit_customer = None


    if "edit_status" not in st.session_state:

        st.session_state.edit_status = "Draft"



    # ===============================
    # HEADER
    # ===============================


    st.markdown(
        """
        <div class="quote-header">

        <h2>
        💼 Quotations
        </h2>

        Create and manage customer quotations

        </div>
        """,

        unsafe_allow_html=True
    )

    # =====================================================
    # LOAD DATA
    # =====================================================


    df = get_quotations()


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
        f"{row.name} ({row.company})"

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
    # EDIT LOAD
    # =====================================================


    if (

        st.session_state.edit_id

        and

        not st.session_state.edit_loaded

    ):



        row = df[
            df["id"]
            ==
            st.session_state.edit_id
        ]



        if not row.empty:


            data = row.iloc[0]



            try:

                st.session_state.quote_items = json.loads(
                    data["items"]
                )

            except:

                st.session_state.quote_items = []



            st.session_state.edit_customer = (

                data["customer_name"]

            )



            st.session_state.edit_status = (

                data["status"]

            )



        st.session_state.edit_loaded = True




    # =====================================================
    # SUMMARY
    # =====================================================


    total_quotes = len(df)



    s1,s2,s3 = st.columns(3)



    with s1:

        st.markdown(

            f"""

            <div class="summary-card">

            Total Quotes

            <div class="summary-number">

            {total_quotes}

            </div>

            </div>

            """,

            unsafe_allow_html=True

        )



    with s2:


        st.markdown(

            """

            <div class="summary-card">

            Module

            <div class="summary-number">

            CRM

            </div>

            </div>

            """,

            unsafe_allow_html=True

        )



    with s3:


        st.markdown(

            """

            <div class="summary-card">

            Version

            <div class="summary-number">

            V1

            </div>

            </div>

            """,

            unsafe_allow_html=True

        )




    st.divider()



    # =====================================================
    # TITLE
    # =====================================================


    if st.session_state.edit_id:


        st.subheader(
            "✏️ Edit Quotation"
        )


    else:


        st.subheader(
            "➕ New Quotation"
        )



    # =====================================================
    # CUSTOMER / STATUS
    # =====================================================



    c1,c2 = st.columns(2)



    default_customer = customer_options[0]



    if st.session_state.edit_customer:


        for key,value in customer_map.items():


            if value == st.session_state.edit_customer:


                default_customer = key

                break



    with c1:


        customer_id = st.selectbox(

            "Customer",

            customer_options,

            index=customer_options.index(
                default_customer
            ),

            format_func=lambda x:
            customer_map[x],

            key="customer_select"

        )



    with c2:


        status_list = [

            "Draft",
            "Sent",
            "Approved",
            "Rejected"

        ]



        status = st.selectbox(

            "Status",

            status_list,

            index=status_list.index(

                st.session_state.edit_status

            ),

            key="status_select"

        )



    st.divider()



    # =====================================================
    # ITEMS
    # =====================================================


    st.subheader(
        "🛒 Items"
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

            key="add_item"

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
                "Enter item description"
            )

    # =====================================================
    # ITEM LIST
    # =====================================================


    subtotal = 0


    updated_items = []



    if st.session_state.quote_items:



        h1,h2,h3,h4 = st.columns(
            [4,1,2,1]
        )


        h1.write("**Item**")
        h2.write("**Qty**")
        h3.write("**Price**")
        h4.write("**Remove**")



        for index,row in enumerate(
            st.session_state.quote_items
        ):



            a,b,c,d = st.columns(
                [4,1,2,1]
            )



            item_name = a.text_input(

                "item",

                value=row["item"],

                key=f"item_{index}",

                label_visibility="collapsed"

            )



            item_qty = b.number_input(

                "qty",

                value=float(row["qty"]),

                min_value=1.0,

                key=f"qty_{index}",

                label_visibility="collapsed"

            )



            item_price = c.number_input(

                "price",

                value=float(row["price"]),

                min_value=0.0,

                key=f"price_{index}",

                label_visibility="collapsed"

            )



            subtotal += (
                item_qty *
                item_price
            )



            remove = d.button(

                "❌",

                key=f"remove_{index}"

            )



            if not remove:


                updated_items.append(

                    {

                        "item":item_name,

                        "qty":item_qty,

                        "price":item_price

                    }

                )



        st.session_state.quote_items = updated_items



    else:


        st.info(
            "No items added"
        )



    st.divider()



    # =====================================================
    # TOTAL CALCULATION
    # =====================================================


    c1,c2 = st.columns(2)



    with c1:


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

        (
            subtotal *
            discount /
            100
        )

    )



    total = (

        after_discount +

        (
            after_discount *
            tax /
            100
        )

    )



    with c2:


        st.markdown(

            f"""

            <div class="summary-card">


            Subtotal

            <h3>

            {subtotal:,.2f}

            </h3>


            Total

            <h2>

            {total:,.2f}

            </h2>


            </div>

            """,

            unsafe_allow_html=True

        )



    st.divider()



    # =====================================================
    # SAVE
    # =====================================================


    if st.button(

        "💾 Save Quotation",

        key="save_quote"

    ):



        if not st.session_state.quote_items:


            st.warning(

                "Please add at least one item"

            )

            st.stop()



        customer_name = customer_map[
            customer_id
        ]



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
                "Quotation updated"
            )



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
                "Quotation saved"
            )



        reset_quote()


        st.rerun()
            # =====================================================
    # QUOTATION LIST
    # =====================================================


    st.divider()


    st.subheader(
        "📋 Recent Quotations"
    )



    df = get_quotations()



    if df.empty:


        st.info(
            "No quotations found"
        )



    else:



        # -----------------------------
        # Search
        # -----------------------------


        search = st.text_input(
            "🔍 Search Customer"
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



        # -----------------------------
        # Table Header
        # -----------------------------


        h1,h2,h3,h4,h5 = st.columns(

            [
                1.2,
                3.5,
                2,
                1.5,
                2

            ]

        )



        h1.markdown(
            "**Quote**"
        )


        h2.markdown(
            "**Customer**"
        )


        h3.markdown(
            "**Amount**"
        )


        h4.markdown(
            "**Status**"
        )


        h5.markdown(
            "**Actions**"
        )



        st.markdown(
            "<hr style='margin:4px 0'>",
            unsafe_allow_html=True
        )



        # -----------------------------
        # Rows
        # -----------------------------


        for _,row in df.iterrows():



            c1,c2,c3,c4,c5 = st.columns(

                [
                    1.2,
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



            c4.markdown(

                f"""

                <span style="
                background:#e2e8f0;
                padding:4px 10px;
                border-radius:15px;
                font-size:12px;">

                {row['status']}

                </span>

                """,

                unsafe_allow_html=True

            )



            with c5:



                b1,b2,b3 = st.columns(3)



                # EDIT
                with b1:


                    if st.button(

                        "✏️",

                        key=f"edit_{row['id']}"

                    ):


                        st.session_state.edit_id = row["id"]

                        st.session_state.edit_loaded = False

                        st.rerun()



                # DELETE

                with b2:


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

                with b3:



                    data = row.to_dict()



                    try:


                        if isinstance(
                            data["items"],
                            str
                        ):

                            data["items"] = json.loads(
                                data["items"]
                            )


                    except:


                        data["items"] = []



                    pdf = generate_quotation_pdf(
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
            
