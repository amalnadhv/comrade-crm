import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

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
# PAGE
# =====================================================

def quotations_page():


    # =================================================
    # STYLE
    # =================================================


    st.markdown(
        """
        <style>


        .quote-header {

            background:
            linear-gradient(
            135deg,
            #ffffff,
            #eff6ff
            );

            padding:25px;

            border-radius:18px;

            border:1px solid #dbeafe;

            margin-bottom:20px;

        }


        .stat-box {

            background:white;

            border-radius:15px;

            padding:15px;

            border:1px solid #e5e7eb;

            text-align:center;

        }


        .stat-number {

            font-size:26px;

            font-weight:bold;

        }


        .quote-line {

            padding:8px 5px;

        }


        </style>

        """,

        unsafe_allow_html=True
    )



    # =================================================
    # SESSION
    # =================================================


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


    if "saving_quote" not in st.session_state:

        st.session_state.saving_quote = False



    # =================================================
    # HEADER
    # =================================================


    st.markdown(
        """
        <div class="quote-header">

        <h1>
        💼 Quotations
        </h1>

        <p>
        Create, manage and track customer quotations
        </p>

        </div>

        """,

        unsafe_allow_html=True
    )



    # =================================================
    # LOAD DATA
    # =================================================


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


        r.id:
        f"{r.name} ({r.company})"


        for r in customers.itertuples()

    }



    customer_options = list(
        customer_map.keys()
    )


    if not customer_options:

        st.warning(
            "Please add customers first"
        )

        return



    # =================================================
    # SUMMARY
    # =================================================


    s1,s2,s3 = st.columns(3)



    with s1:

        st.markdown(

            f"""

            <div class="stat-box">

            Total Quotes

            <div class="stat-number">

            {len(df)}

            </div>

            </div>

            """,

            unsafe_allow_html=True

        )



    with s2:

        st.markdown(

            """

            <div class="stat-box">

            Module

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

            <div class="stat-box">

            Status

            <div class="stat-number">

            Active

            </div>

            </div>

            """,

            unsafe_allow_html=True

        )
            # =====================================================
    # CREATE NEW
    # =====================================================


    st.divider()


    if st.button(
        "➕ Create New Quotation",
        key="new_quote"
    ):


        st.session_state.edit_id = None

        st.session_state.quote_items = []

        st.session_state.edit_loaded = False

        st.session_state.edit_customer = None

        st.session_state.edit_status = "Draft"

        st.rerun()



    # =====================================================
    # LOAD EDIT DATA
    # =====================================================


    if (

        st.session_state.edit_id

        and

        not st.session_state.edit_loaded

    ):


        match = df[
            df["id"]
            ==
            st.session_state.edit_id
        ]


        if not match.empty:


            row = match.iloc[0]


            try:

                st.session_state.quote_items = json.loads(
                    row["items"]
                )


            except:

                st.session_state.quote_items = []



            st.session_state.edit_customer = (
                row["customer_name"]
            )


            st.session_state.edit_status = (
                row["status"]
            )



        st.session_state.edit_loaded = True



    # =====================================================
    # FORM TITLE
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


    default_customer = customer_options[0]



    if st.session_state.edit_customer:


        default_customer = next(

            (

                k

                for k,v in customer_map.items()

                if v ==
                st.session_state.edit_customer

            ),

            customer_options[0]

        )



    c1,c2 = st.columns(2)



    with c1:


        customer_id = st.selectbox(

            "Customer",

            customer_options,

            index=
            customer_options.index(
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

                if st.session_state.edit_status in status_list

                else "Draft"

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



    a,b,c,d = st.columns(
        [4,1,2,1]
    )



    with a:

        item_input = st.text_input(
            "Item",
            key="item_input"
        )



    with b:

        qty_input = st.number_input(

            "Qty",

            min_value=1.0,

            value=1.0,

            key="qty_input"

        )



    with c:

        price_input = st.number_input(

            "Price",

            min_value=0.0,

            value=0.0,

            key="price_input"

        )



    with d:

        st.write("")

        add_item = st.button(
            "➕",
            key="add_item"
        )



    if add_item:


        if item_input.strip():


            st.session_state.quote_items.append(

                {

                    "item": item_input,

                    "qty": qty_input,

                    "price": price_input

                }

            )


            st.rerun()



        else:

            st.warning(
                "Enter item name"
            )



    subtotal = 0

    updated_items = []



    for i,it in enumerate(
        st.session_state.quote_items
    ):


        x1,x2,x3,x4 = st.columns(
            [4,1,2,1]
        )



        new_item = x1.text_input(

            "Item",

            it["item"],

            key=f"item_{i}"

        )



        new_qty = x2.number_input(

            "Qty",

            value=float(it["qty"]),

            key=f"qty_{i}"

        )



        new_price = x3.number_input(

            "Price",

            value=float(it["price"]),

            key=f"price_{i}"

        )



        subtotal += (
            new_qty *
            new_price
        )



        if not x4.button(

            "❌",

            key=f"remove_{i}"

        ):


            updated_items.append(

                {

                    "item":new_item,

                    "qty":new_qty,

                    "price":new_price

                }

            )



    st.session_state.quote_items = updated_items



    st.divider()



    # =====================================================
    # TOTAL
    # =====================================================


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

        subtotal *
        discount /
        100

    )



    total = (

        after_discount +

        after_discount *
        tax /
        100

    )



    st.success(
        f"Total Amount : {total:,.2f}"
    )



    # =====================================================
    # SAVE
    # =====================================================


    if st.button(

        "💾 Save Quotation",

        key="save_quote"

    ):



        if st.session_state.saving_quote:


            st.warning(
                "Please wait..."
            )

            st.stop()



        if not st.session_state.quote_items:


            st.warning(
                "Please add item before saving"
            )

            st.stop()



        st.session_state.saving_quote = True



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



            st.session_state.edit_id = None



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



        st.session_state.quote_items = []

        st.session_state.edit_loaded = False

        st.session_state.saving_quote = False


        st.rerun()
            # =====================================================
    # QUOTATION LIST
    # =====================================================


    st.divider()


    st.subheader(
        "📋 All Quotations"
    )



    df = get_quotations()



    if df.empty:


        st.info(
            "No quotations found"
        )



    else:



        # Search

        search = st.text_input(
            "🔍 Search quotation"
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



        # Header


        h1,h2,h3,h4,h5 = st.columns(

            [
                1.2,
                3.5,
                2,
                1.5,
                2

            ]

        )


        h1.markdown("**Quote**")

        h2.markdown("**Customer**")

        h3.markdown("**Amount**")

        h4.markdown("**Status**")

        h5.markdown("**Action**")



        st.markdown(
            "<hr style='margin:5px 0'>",
            unsafe_allow_html=True
        )



        status_color = {

            "Draft":"#64748b",

            "Sent":"#2563eb",

            "Approved":"#16a34a",

            "Rejected":"#dc2626"

        }



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



            c1.markdown(

                f"""

                <span style="
                background:#dbeafe;
                color:#1d4ed8;
                padding:5px 10px;
                border-radius:15px;
                font-weight:bold">

                QT-{row['id']:04d}

                </span>

                """,

                unsafe_allow_html=True

            )



            c2.write(

                row["customer_name"]

            )



            c3.markdown(

                f"""

                <b style="
                color:#059669">

                {row['total']:,.2f}

                </b>

                """,

                unsafe_allow_html=True

            )



            status = row["status"]



            c4.markdown(

                f"""

                <span style="
                background:{status_color.get(status,'#64748b')};
                color:white;
                padding:4px 10px;
                border-radius:15px;
                font-size:12px">

                {status}

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


                    safe_row = row.to_dict()


                    items = safe_row.get(
                        "items",
                        []
                    )


                    if isinstance(
                        items,
                        str
                    ):


                        try:

                            items = json.loads(
                                items
                            )

                        except:

                            items = []



                    safe_row["items"] = items



                    pdf_buffer = generate_quotation_pdf(
                        safe_row
                    )



                    st.download_button(

                        "📄",

                        pdf_buffer,

                        file_name=
                        f"quotation_{row['id']}.pdf",

                        mime=
                        "application/pdf",

                        key=
                        f"pdf_{row['id']}"

                    )



            st.markdown(

                "<hr style='margin:3px 0'>",

                unsafe_allow_html=True

            )
            
