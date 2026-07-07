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



    clear_keys = [

        "item_input",
        "qty_input",
        "price_input",
        "discount",
        "tax",
        "customer_select",
        "status_select"

    ]


    for key in clear_keys:


        if key in st.session_state:

            del st.session_state[key]



# =====================================================
# QUOTATIONS PAGE
# =====================================================

def quotations_page():


    # =================================================
    # STYLE
    # =================================================


    st.markdown(
        """
        <style>


        .quote-header {

            background:white;
            padding:20px;
            border-radius:14px;
            border:1px solid #e5e7eb;
            margin-bottom:15px;

        }


        .total-box {

            background:#f8fafc;
            padding:18px;
            border-radius:12px;
            border:1px solid #e5e7eb;

        }


        .amount-text {

            font-size:24px;
            font-weight:bold;

        }


        </style>
        """,

        unsafe_allow_html=True

    )



    # =================================================
    # SESSION DEFAULTS
    # =================================================


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



    # =================================================
    # HEADER
    # =================================================


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



    # =================================================
    # LOAD CUSTOMERS
    # =================================================


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



    customer_options=list(
        customer_map.keys()
    )



    if not customer_options:

        st.warning(
            "Please create customers first"
        )

        return



    # =================================================
    # NEW BUTTON
    # =================================================


    if st.button(
        "➕ New Quotation",
        width="content"
    ):


        reset_quote()

        st.rerun()



    # =================================================
    # LOAD EDIT DATA
    # =================================================


    quotations = get_quotations()



    if (
        st.session_state.edit_id
        and
        not st.session_state.edit_loaded
    ):


        row = quotations[
            quotations["id"]
            ==
            st.session_state.edit_id
        ]



        if not row.empty:


            data=row.iloc[0]


            try:

                st.session_state.quote_items = json.loads(
                    data["items"]
                )

            except:

                st.session_state.quote_items=[]



            st.session_state.edit_customer = (
                data["customer_name"]
            )


            st.session_state.edit_status = (
                data["status"]
            )



        st.session_state.edit_loaded=True



    if st.session_state.edit_id:

        st.subheader(
            "✏ Edit Quotation"
        )

    else:

        st.subheader(
            "➕ New Quotation"
        )



    # =================================================
    # CUSTOMER / STATUS
    # =================================================


    col1,col2 = st.columns(2)



    default_customer = customer_options[0]



    if st.session_state.edit_customer:


        for key,value in customer_map.items():

            if value == st.session_state.edit_customer:

                default_customer=key

                break




    with col1:


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



    with col2:


        status_list=[

            "Draft",
            "Sent",
            "Approved",
            "Rejected"

        ]


        status = st.selectbox(

            "Status",

            status_list,

            index=
            status_list.index(
                st.session_state.edit_status
            ),

            key="status_select"

        )



    st.divider()

    # =================================================
    # ITEMS
    # =================================================


    st.subheader(
        "🛒 Items"
    )



    c1,c2,c3,c4 = st.columns(
        [4,1,2,1]
    )


    with c1:

        item = st.text_input(
            "Description",
            key="item_input"
        )


    with c2:

        qty = st.number_input(
            "Qty",
            min_value=1.0,
            value=1.0,
            key="qty_input"
        )


    with c3:

        price = st.number_input(
            "Price",
            min_value=0.0,
            value=0.0,
            key="price_input"
        )


    with c4:

        st.write("")

        add_item = st.button(
            "➕",
            width="content"
        )



    if add_item:


        if item.strip():


            st.session_state.quote_items.append(

                {
                    "item": item,
                    "qty": qty,
                    "price": price
                }

            )

            st.rerun()


        else:

            st.warning(
                "Enter item description"
            )



    st.divider()



    # =================================================
    # ITEM GRID
    # =================================================


    subtotal = 0


    updated_items=[]



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



            name=a.text_input(

                "item",

                value=row["item"],

                key=f"edit_item_{index}",

                label_visibility="collapsed"

            )



            quantity=b.number_input(

                "qty",

                value=float(row["qty"]),

                min_value=1.0,

                key=f"edit_qty_{index}",

                label_visibility="collapsed"

            )



            rate=c.number_input(

                "price",

                value=float(row["price"]),

                min_value=0.0,

                key=f"edit_price_{index}",

                label_visibility="collapsed"

            )



            subtotal += quantity * rate



            remove = d.button(

                "❌",

                key=f"remove_{index}"

            )



            if not remove:


                updated_items.append(

                    {
                        "item":name,
                        "qty":quantity,
                        "price":rate
                    }

                )



        st.session_state.quote_items = updated_items



    else:


        st.info(
            "No items added"
        )



    st.divider()



    # =================================================
    # TOTALS
    # =================================================


    left,right = st.columns(2)



    with left:


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



    with right:


        st.markdown(

            f"""

            <div class="total-box">


            Subtotal :

            <b>{subtotal:,.2f}</b>


            <br>

            Discount :

            <b>{discount}%</b>


            <br>

            Tax :

            <b>{tax}%</b>


            <hr>


            <div class="amount-text">

            Total : {total:,.2f}

            </div>


            </div>


            """,

            unsafe_allow_html=True

        )



    st.divider()



    # =================================================
    # SAVE
    # =================================================


    if st.button(

        "💾 Save Quotation",

        width="stretch"

    ):



        if not st.session_state.quote_items:


            st.warning(
                "Please add at least one item before saving"
            )

            st.stop()



        customer_name = customer_map[customer_id]



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

    # =================================================
    # QUOTATION LIST
    # =================================================


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


        # Header row


        h1,h2,h3,h4,h5 = st.columns(
            [1.3,3.5,2,1.5,2]
        )


        h1.markdown("**Quote No**")
        h2.markdown("**Customer**")
        h3.markdown("**Amount**")
        h4.markdown("**Status**")
        h5.markdown("**Actions**")



        st.markdown(
            "<hr style='margin:3px 0'>",
            unsafe_allow_html=True
        )



        for _,row in df.iterrows():



            c1,c2,c3,c4,c5 = st.columns(
                [1.3,3.5,2,1.5,2]
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



            status=row["status"]



            c4.markdown(

                f"""

                <span style="
                background:#e5e7eb;
                padding:3px 8px;
                border-radius:12px;
                font-size:12px;">

                {status}

                </span>

                """,

                unsafe_allow_html=True

            )



            with c5:



                b1,b2,b3 = st.columns(
                    [1,1,1]
                )



                # EDIT

                with b1:


                    if st.button(

                        "✏️",

                        key=f"edit_{row['id']}",

                        width="content"

                    ):


                        st.session_state.edit_id = row["id"]

                        st.session_state.edit_loaded=False

                        st.rerun()



                # DELETE

                with b2:


                    if st.button(

                        "🗑",

                        key=f"delete_{row['id']}",

                        width="content"

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



                    data=row.to_dict()



                    items=data.get(
                        "items",
                        []
                    )



                    if isinstance(
                        items,
                        str
                    ):


                        try:

                            items=json.loads(
                                items
                            )


                        except:

                            items=[]



                    data["items"]=items



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
                        f"pdf_{row['id']}",

                        width="content"

                    )



            st.markdown(

                "<hr style='margin:2px 0'>",

                unsafe_allow_html=True

            )
            
