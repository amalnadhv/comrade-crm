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
# CLEAR FORM
# =====================================================

def reset_quote():

    # clear quotation data

    st.session_state.quote_items = []


    # clear edit mode

    st.session_state.edit_id = None

    st.session_state.edit_loaded = False

    st.session_state.edit_customer = None

    st.session_state.edit_status = "Draft"



    # clear input widgets

    widget_keys = [

        "item_input",

        "qty_input",

        "price_input",

        "discount",

        "tax",

        "customer_select",

        "status_select"

    ]


    for key in widget_keys:

        if key in st.session_state:

            del st.session_state[key]

# =====================================================
# PAGE
# =====================================================

def quotations_page():


    # ---------------- STYLE ----------------

    st.markdown(
        """
        <style>

        .header-box {

            background:white;
            padding:25px;
            border-radius:15px;
            margin-bottom:20px;

        }


        .card {

            background:white;
            padding:18px;
            border-radius:12px;
            border:1px solid #eeeeee;
            margin-bottom:15px;

        }


        .total-card {

            background:#f1f5f9;
            padding:20px;
            border-radius:15px;
            text-align:right;

        }


        .total-value {

            font-size:28px;
            font-weight:bold;

        }


        </style>
        """,
        unsafe_allow_html=True
    )



    # ---------------- SESSION ----------------


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



    # ---------------- HEADER ----------------


    st.markdown(
        """
        <div class="header-box">

        <h1>
        💼 Quotations
        </h1>

        Create and manage customer quotations

        </div>
        """,
        unsafe_allow_html=True
    )



    # ---------------- DATA ----------------


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


    customer_options = list(customer_map.keys())


    if not customer_options:

        st.warning(
            "Please add customers first"
        )

        return



    # ---------------- NEW BUTTON ----------------


    if st.button(
        "➕ New Quotation"
    ):

        reset_quote()

        st.rerun()



    # ---------------- EDIT LOAD ----------------


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



    if st.session_state.edit_id:

        st.subheader(
            "✏ Edit Quotation"
        )

    else:

        st.subheader(
            "➕ New Quotation"
        )



    # ---------------- CUSTOMER ----------------


    c1,c2 = st.columns(2)


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

        status = st.selectbox(

            "Status",

            [
                "Draft",
                "Sent",
                "Approved",
                "Rejected"
            ],

            index=[
                "Draft",
                "Sent",
                "Approved",
                "Rejected"
            ].index(
                st.session_state.edit_status
            ),

            key="status_select"

        )


    st.divider()


    # ---------------- ITEMS ----------------


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

        add = st.button(
            "➕"
        )


    if add:

        if item:

            st.session_state.quote_items.append(
                {
                    "item":item,
                    "qty":qty,
                    "price":price
                }
            )

            st.rerun()


    # =====================================================
    # ITEM TABLE
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



        for index,item in enumerate(
            st.session_state.quote_items
        ):


            a,b,c,d = st.columns(
                [4,1,2,1]
            )


            new_item = a.text_input(
                "item",
                value=item["item"],
                key=f"item_edit_{index}",
                label_visibility="collapsed"
            )


            new_qty = b.number_input(
                "qty",
                value=float(item["qty"]),
                key=f"qty_edit_{index}",
                label_visibility="collapsed"
            )


            new_price = c.number_input(
                "price",
                value=float(item["price"]),
                key=f"price_edit_{index}",
                label_visibility="collapsed"
            )


            amount = new_qty * new_price

            subtotal += amount



            if d.button(
                "❌",
                key=f"remove_item_{index}"
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
            "No items added"
        )



    st.divider()



    # =====================================================
    # TOTAL SECTION
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


            <div class="total-value">

            Total : {total:,.2f}

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
        "Please add at least one item before saving."
    )

else:

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


    reset_quote()

    st.rerun()



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
    # LIST
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


        for _,row in df.iterrows():


            st.markdown(

                f"""

                <div class="card">


                <h3>
                QT-{row['id']:04d}
                </h3>


                <b>
                Customer:
                </b>
                {row['customer_name']}


                <br>


                <b>
                Amount:
                </b>
                {row['total']:,.2f}


                <br>


                <b>
                Status:
                </b>
                {row['status']}


                </div>


                """,

                unsafe_allow_html=True

            )



            e,d,p = st.columns(3)



            with e:


                if st.button(
                    "✏ Edit",
                    key=f"edit_{row['id']}"
                ):

                    st.session_state.edit_id = row["id"]

                    st.session_state.edit_loaded = False

                    st.rerun()



            with d:


                if st.button(
                    "🗑 Delete",
                    key=f"delete_{row['id']}"
                ):


                    delete_quotation(
                        row["id"]
                    )

                    st.success(
                        "Deleted"
                    )

                    st.rerun()



            with p:


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



                pdf = generate_quotation_pdf(
                    safe_row
                )



                st.download_button(

                    "📄 PDF",

                    pdf,

                    file_name=
                    f"quotation_{row['id']}.pdf",

                    mime=
                    "application/pdf",

                    key=
                    f"pdf_{row['id']}"

                )


            st.divider()
            
