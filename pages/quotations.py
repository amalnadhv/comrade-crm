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



# ======================================================
# UPDATE QUOTATION
# ======================================================

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



# ======================================================
# DELETE QUOTATION
# ======================================================

def delete_quotation(qid):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM quotations WHERE id=?",
        (qid,)
    )

    conn.commit()
    conn.close()



# ======================================================
# RESET FORM
# ======================================================

def clear_quote_form():

    keys = [

        "quote_items",

        "customer_select",

        "status_select",

        "item_input",

        "qty_input",

        "price_input",

        "discount",

        "tax"

    ]


    for key in keys:

        if key in st.session_state:

            del st.session_state[key]



    st.session_state.edit_id = None

    st.session_state.edit_loaded = False

    st.session_state.edit_customer = None

    st.session_state.edit_status = "Draft"




# ======================================================
# PAGE
# ======================================================

def quotations_page():



    # ---------------- STYLE ----------------

    st.markdown(
        """
        <style>


        .quote-box {

            background:#ffffff;

            padding:15px;

            border-radius:10px;

            border:1px solid #eeeeee;

            margin-bottom:12px;

        }


        .total-card {

            padding:18px;

            border-radius:12px;

            background:#f5f7fb;

            text-align:right;

        }


        .total-number {

            font-size:26px;

            font-weight:bold;

        }


        </style>
        """,
        unsafe_allow_html=True
    )



    st.title("💼 Quotations")



    # ==================================================
    # SESSION
    # ==================================================


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




    # ==================================================
    # LOAD DATA
    # ==================================================


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
        f"{row.name} ({row.company})"

        for row in customers.itertuples()

    }



    customer_options = list(customer_map.keys())



    if not customer_options:

        st.warning(
            "Please create customers first."
        )

        return




    # ==================================================
    # NEW BUTTON
    # ==================================================


    top1,top2 = st.columns([4,1])



    with top2:


        if st.button(
            "➕ New",
            use_container_width=True
        ):

            clear_quote_form()

            st.rerun()



    # ==================================================
    # LOAD EDIT RECORD
    # ==================================================


    if (

        st.session_state.edit_id

        and

        not st.session_state.edit_loaded

    ):


        record = quotation_df[
            quotation_df["id"]
            ==
            st.session_state.edit_id
        ]



        if not record.empty:


            row = record.iloc[0]



            try:

                st.session_state.quote_items = json.loads(
                    row["items"]
                )

            except:

                st.session_state.quote_items = []



            st.session_state.edit_customer = row["customer_name"]


            st.session_state.edit_status = row["status"]



        st.session_state.edit_loaded = True




    # ==================================================
    # HEADER
    # ==================================================


    if st.session_state.edit_id:

        st.subheader(
            "✏ Edit Quotation"
        )

    else:

        st.subheader(
            "➕ Create Quotation"
        )



    st.divider()



    # ==================================================
    # CUSTOMER
    # ==================================================


    col1,col2 = st.columns(2)



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



    with col1:


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



    with col2:


        status_list = [

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
            )

            if st.session_state.edit_status in status_list

            else 0,

            key="status_select"

        )



    st.divider()
        # ==================================================
    # ITEMS
    # ==================================================

    st.subheader("🛒 Items")


    item_col1, item_col2, item_col3, item_col4 = st.columns(
        [4, 1, 2, 1]
    )


    with item_col1:

        item_input = st.text_input(
            "Item Description",
            key="item_input"
        )


    with item_col2:

        qty_input = st.number_input(
            "Qty",
            min_value=1.0,
            value=1.0,
            key="qty_input"
        )


    with item_col3:

        price_input = st.number_input(
            "Price",
            min_value=0.0,
            value=0.0,
            key="price_input"
        )


    with item_col4:

        st.write("")

        if st.button(
            "➕ Add",
            use_container_width=True
        ):


            if item_input.strip():


                st.session_state.quote_items.append(
                    {
                        "item": item_input,
                        "qty": qty_input,
                        "price": price_input
                    }
                )


                # clear item entry only

                st.session_state.item_input = ""

                st.session_state.qty_input = 1.0

                st.session_state.price_input = 0.0


                st.rerun()



    st.divider()



    # ==================================================
    # ITEM DISPLAY
    # ==================================================


    subtotal = 0


    updated_items = []



    if st.session_state.quote_items:


        h1,h2,h3,h4 = st.columns(
            [4,1,2,1]
        )

        h1.write("**Description**")
        h2.write("**Qty**")
        h3.write("**Price**")
        h4.write("**Remove**")



        for index,item in enumerate(
            st.session_state.quote_items
        ):


            c1,c2,c3,c4 = st.columns(
                [4,1,2,1]
            )



            new_item = c1.text_input(

                "item",

                value=item["item"],

                key=f"edit_item_{index}",

                label_visibility="collapsed"

            )


            new_qty = c2.number_input(

                "qty",

                value=float(item["qty"]),

                key=f"edit_qty_{index}",

                label_visibility="collapsed"

            )


            new_price = c3.number_input(

                "price",

                value=float(item["price"]),

                key=f"edit_price_{index}",

                label_visibility="collapsed"

            )



            amount = new_qty * new_price


            subtotal += amount



            if c4.button(
                "❌",
                key=f"remove_{index}"
            ):

                continue



            updated_items.append(
                {
                    "item":new_item,
                    "qty":new_qty,
                    "price":new_price
                }
            )



        st.session_state.quote_items = updated_items



    else:

        st.info(
            "No items added."
        )



    st.divider()



    # ==================================================
    # TOTALS
    # ==================================================


    col1,col2 = st.columns(2)



    with col1:


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



    with col2:


        st.markdown(

            f"""

            <div class="total-card">


            Subtotal :
            <b>{subtotal:,.2f}</b>


            <br>


            Discount :
            <b>{discount}%</b>


            <br>


            Tax :
            <b>{tax}%</b>


            <hr>


            <div class="total-number">

            Total : {total:,.2f}

            </div>


            </div>

            """,

            unsafe_allow_html=True

        )



    st.divider()



    # ==================================================
    # SAVE
    # ==================================================


    if st.button(

        "💾 Save Quotation",

        use_container_width=True

    ):



        if not st.session_state.quote_items:


            st.warning(
                "Please add items before saving."
            )

            return



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



        # IMPORTANT RESET

        clear_quote_form()



        st.rerun()
            # ==================================================
    # QUOTATION LIST
    # ==================================================

    st.divider()

    st.subheader("📋 Saved Quotations")


    # Always reload fresh data from database

    quotation_df = get_quotations()



    if quotation_df.empty:


        st.info(
            "No quotations saved yet."
        )


    else:


        search = st.text_input(
            "🔍 Search customer",
            key="quotation_search"
        )



        display_df = quotation_df.copy()



        if search:


            display_df = display_df[
                display_df["customer_name"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]



        for _,row in display_df.iterrows():



            st.markdown(

                f"""

                <div class="quote-box">


                <h4>
                📄 Quotation No : QT-{row['id']:04d}
                </h4>


                <b>Customer:</b>
                {row['customer_name']}


                <br>


                <b>Total:</b>
                {row['total']:,.2f}


                <br>


                <b>Status:</b>
                {row['status']}


                </div>

                """,

                unsafe_allow_html=True

            )



            c1,c2,c3 = st.columns(3)



            # ---------------- EDIT ----------------

            with c1:


                if st.button(

                    "✏ Edit",

                    key=f"edit_{row['id']}",

                    use_container_width=True

                ):


                    st.session_state.edit_id = row["id"]

                    st.session_state.edit_loaded = False

                    st.session_state.edit_customer = None

                    st.rerun()



            # ---------------- DELETE ----------------


            with c2:


                if st.button(

                    "🗑 Delete",

                    key=f"delete_{row['id']}",

                    use_container_width=True

                ):


                    delete_quotation(
                        row["id"]
                    )


                    st.success(
                        "Quotation deleted"
                    )


                    st.rerun()



            # ---------------- PDF ----------------


            with c3:


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



                pdf_file = generate_quotation_pdf(
                    safe_row
                )



                st.download_button(

                    "📄 PDF",

                    data=pdf_file,

                    file_name=
                    f"QT-{row['id']:04d}.pdf",

                    mime=
                    "application/pdf",

                    key=
                    f"pdf_{row['id']}",

                    use_container_width=True

                )



            st.divider()
            
