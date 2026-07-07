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


    for k in keys:

        if k in st.session_state:

            del st.session_state[k]
            def quotations_page():


    # =====================================================
    # STYLE
    # =====================================================

    st.markdown(
        """
        <style>

        .quote-header {

            background:linear-gradient(
                135deg,
                #ffffff,
                #f8fafc
            );

            padding:20px;
            border-radius:14px;
            border:1px solid #e5e7eb;
            margin-bottom:15px;

        }


        .small-card {

            background:white;
            border:1px solid #e5e7eb;
            border-radius:10px;
            padding:10px 14px;
            margin-bottom:8px;

        }


        .amount {

            font-size:20px;
            font-weight:700;

        }


        .total-box {

            background:#f8fafc;
            padding:18px;
            border-radius:12px;
            border:1px solid #e5e7eb;

        }


        </style>
        """,
        unsafe_allow_html=True
    )



    # =====================================================
    # SESSION
    # =====================================================


    defaults = {

        "quote_items": [],
        "edit_id": None,
        "edit_loaded": False,
        "edit_customer": None,
        "edit_status": "Draft"

    }


    for key,value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value



    # =====================================================
    # HEADER
    # =====================================================


    st.markdown(
        """
        <div class="quote-header">

        <h2>
        💼 Quotations
        </h2>

        Manage customer quotations easily

        </div>

        """,
        unsafe_allow_html=True
    )



    # =====================================================
    # LOAD DATA
    # =====================================================


    quotation_df = get_quotations()


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


    customer_options = list(customer_map.keys())



    if not customer_options:

        st.warning(
            "Please create customers before making quotations"
        )

        return



    # =====================================================
    # NEW BUTTON
    # =====================================================


    top1,top2 = st.columns([1,5])


    with top1:

        if st.button(
            "➕ New",
            use_container_width=True
        ):

            reset_quote()
            st.rerun()



    # =====================================================
    # LOAD EDIT DATA
    # =====================================================


    if (
        st.session_state.edit_id
        and
        not st.session_state.edit_loaded
    ):


        row = quotation_df[
            quotation_df.id ==
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
            "➕ Create Quotation"
        )



    # =====================================================
    # CUSTOMER SECTION
    # =====================================================


    c1,c2 = st.columns(2)


    default_customer = customer_options[0]


    if st.session_state.edit_customer:


        for k,v in customer_map.items():

            if v == st.session_state.edit_customer:

                default_customer=k
                break



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
        # =====================================================
    # ITEMS
    # =====================================================

    st.subheader("🛒 Items")


    a,b,c,d = st.columns(
        [4,1,2,1]
    )


    with a:

        item = st.text_input(
            "Description",
            key="item_input"
        )


    with b:

        qty = st.number_input(
            "Qty",
            min_value=1.0,
            value=1.0,
            key="qty_input"
        )


    with c:

        price = st.number_input(
            "Price",
            min_value=0.0,
            value=0.0,
            key="price_input"
        )


    with d:

        st.write("")

        add_item = st.button(
            "➕",
            use_container_width=True
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



    st.divider()



    # =====================================================
    # ITEM LIST
    # =====================================================


    subtotal=0

    updated=[]



    if st.session_state.quote_items:


        header = st.columns(
            [4,1,2,1]
        )

        header[0].markdown("**Item**")
        header[1].markdown("**Qty**")
        header[2].markdown("**Price**")
        header[3].markdown("**❌**")



        for i,row in enumerate(
            st.session_state.quote_items
        ):


            c1,c2,c3,c4 = st.columns(
                [4,1,2,1]
            )


            name=c1.text_input(

                "item",

                value=row["item"],

                key=f"edit_item_{i}",

                label_visibility="collapsed"

            )



            q=c2.number_input(

                "qty",

                value=float(row["qty"]),

                min_value=1.0,

                key=f"edit_qty_{i}",

                label_visibility="collapsed"

            )



            p=c3.number_input(

                "price",

                value=float(row["price"]),

                min_value=0.0,

                key=f"edit_price_{i}",

                label_visibility="collapsed"

            )



            subtotal += q*p



            remove = c4.button(

                "❌",

                key=f"remove_{i}"

            )



            if not remove:


                updated.append(

                    {
                        "item":name,
                        "qty":q,
                        "price":p
                    }

                )



        st.session_state.quote_items = updated



    else:


        st.info(
            "No items added yet"
        )



    st.divider()



    # =====================================================
    # TOTAL CALCULATION
    # =====================================================


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



    with right:


        st.markdown(

            f"""

            <div class="total-box">

            Sub Total :
            <b>{subtotal:,.2f}</b>

            <br>

            Discount :
            <b>{discount}%</b>

            <br>

            Tax :
            <b>{tax}%</b>

            <hr>

            <div class="amount">

            Total :
            {total:,.2f}

            </div>

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

        use_container_width=True

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
                "Quotation updated successfully"
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
                "Quotation saved successfully"
            )



        reset_quote()

        st.rerun()
    
        # =====================================================
    # COMPACT QUOTATION LIST
    # =====================================================

    st.divider()

    st.subheader("📋 Quotations")


    df = get_quotations()


    if df.empty:

        st.info("No quotations found")


    else:


        # Header

        h1,h2,h3,h4,h5 = st.columns(
            [1.2,3.5,2,1.5,2]
        )


        h1.markdown("**Quote No**")
        h2.markdown("**Customer**")
        h3.markdown("**Amount**")
        h4.markdown("**Status**")
        h5.markdown("**Action**")


        st.markdown(
            "<hr style='margin:3px 0'>",
            unsafe_allow_html=True
        )



        for _,row in df.iterrows():


            c1,c2,c3,c4,c5 = st.columns(
                [1.2,3.5,2,1.5,2]
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
                border-radius:10px;
                font-size:11px;">
                {status}
                </span>
                """,
                unsafe_allow_html=True
            )



            with c5:


                b1,b2,b3 = st.columns(
                    [1,1,1]
                )


                with b1:

                    if st.button(
                        "✏️",
                        key=f"edit_{row['id']}",
                        width="content"
                    ):

                        st.session_state.edit_id = row["id"]

                        st.session_state.edit_loaded = False

                        st.rerun()



                with b2:

                    if st.button(
                        "🗑",
                        key=f"del_{row['id']}",
                        width="content"
                    ):

                        delete_quotation(
                            row["id"]
                        )

                        st.success(
                            "Deleted"
                        )

                        st.rerun()



                with b3:


                    safe_row=row.to_dict()


                    items=safe_row.get(
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



                    safe_row["items"]=items



                    pdf=generate_quotation_pdf(
                        safe_row
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
