import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf


DB_NAME = "crm.db"



# ================= UPDATE =================

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



# ================= DELETE =================

def delete_quotation(qid):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()


    cur.execute(
        "DELETE FROM quotations WHERE id=?",
        (qid,)
    )


    conn.commit()
    conn.close()



# ================= PAGE =================

def quotations_page():


    # ================= STYLE =================


    st.markdown(
        """
        <style>


        .quote-header {

            background:
            linear-gradient(
            135deg,
            #eff6ff,
            #ffffff
            );

            padding:25px;

            border-radius:18px;

            border:1px solid #dbeafe;

            margin-bottom:20px;

        }


        .quote-card {

            background:white;

            border-radius:12px;

            padding:8px;

            border-bottom:1px solid #e5e7eb;

        }


        .status-badge {

            padding:5px 12px;

            border-radius:15px;

            color:white;

            font-size:12px;

        }


        </style>
        """,

        unsafe_allow_html=True
    )



    st.markdown(
        """
        <div class="quote-header">

        <h1>💼 Quotations</h1>

        <p>
        Create, manage and track customer quotations
        </p>

        </div>
        """,

        unsafe_allow_html=True
    )



    # ================= SESSION INIT =================


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



    # ================= DATA =================


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



    # ================= CREATE NEW =================


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



    # ================= LOAD EDIT =================


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



            st.session_state.edit_customer = row["customer_name"]

            st.session_state.edit_status = row["status"]



        st.session_state.edit_loaded = True



    # ================= MODE =================


    st.subheader(

        "🟠 Edit Quotation"

        if st.session_state.edit_id

        else

        "🔵 Create New Quotation"

    )



    default_customer = customer_options[0]



    if st.session_state.edit_id:


        default_customer = next(

            (

                k

                for k,v in customer_map.items()

                if v ==
                st.session_state.edit_customer

            ),

            customer_options[0]

        )



    # ================= CUSTOMER =================


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



    status_list = [

        "Draft",
        "Sent",
        "Approved",
        "Rejected"

    ]


    status = st.selectbox(

        "Status",

        status_list,

        index=(

            status_list.index(
                st.session_state.edit_status
            )

            if st.session_state.edit_status in status_list

            else 0

        ),

        key="status_select"

    )



    # ================= ITEMS =================


    st.markdown("### 🛒 Items")



    item_input = st.text_input(

        "Item",

        key="item_input"

    )



    qty_input = st.number_input(

        "Qty",

        value=1.0,

        key="qty_input"

    )



    price_input = st.number_input(

        "Price",

        value=0.0,

        key="price_input"

    )



    if st.button(

        "➕ Add Item",

        key="add_item"

    ):


        st.session_state.quote_items.append(

            {

                "item":item_input,

                "qty":qty_input,

                "price":price_input

            }

        )


        st.rerun()



    subtotal = 0

    updated_items = []



    for i,it in enumerate(

        st.session_state.quote_items

    ):



        cols = st.columns(

            [3,2,2,1]

        )



        new_item = cols[0].text_input(

            "Item",

            it["item"],

            key=f"it_{i}"

        )



        new_qty = cols[1].number_input(

            "Qty",

            value=float(it["qty"]),

            key=f"qt_{i}"

        )



        new_price = cols[2].number_input(

            "Price",

            value=float(it["price"]),

            key=f"pr_{i}"

        )



        subtotal += (

            new_qty *

            new_price

        )



        if cols[3].button(

            "❌",

            key=f"rm_{i}"

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



    st.divider()



    # ================= TOTAL =================


    discount = st.number_input(

        "Discount %",

        value=0.0,

        key="discount"

    )



    tax = st.number_input(

        "Tax %",

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



    st.success(

        f"Subtotal : {subtotal:,.2f}"

    )


    st.success(

        f"Total : {total:,.2f}"

    )

  # ================= CANCEL EDIT =================

  if st.session_state.edit_id:

      if st.button(
          "❌ Cancel Edit",
          key="cancel_edit"
      ):

        st.session_state.edit_id = None

        st.session_state.quote_items = []

        st.session_state.edit_loaded = False

        st.session_state.edit_customer = None

        st.session_state.edit_status = "Draft"


        # clear widgets

        for key in [
            "customer_select",
            "status_select",
            "item_input",
            "qty_input",
            "price_input",
            "discount",
            "tax"
        ]:

            if key in st.session_state:

                del st.session_state[key]


        st.rerun()

    # ================= SAVE =================


    if st.button(

        "💾 Save Quotation",

        key="save_quote"

    ):


        if st.session_state.saving_quote:


            st.warning(
                "Saving already in progress"
            )

            st.stop()



        if not st.session_state.quote_items:


            st.warning(
                "Please add at least one item"
            )

            st.stop()



        st.session_state.saving_quote = True



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


        st.session_state.edit_id = None

        st.session_state.edit_loaded = False

        st.session_state.edit_customer = None

        st.session_state.edit_status = "Draft"



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



    st.session_state.quote_items = []

    st.session_state.saving_quote = False


    st.rerun()



    # =====================================================
    # COMPACT QUOTATION LIST
    # =====================================================


    st.divider()


    st.subheader(
        "📋 Quotations"
    )


    df = get_quotations()



    if df.empty:


        st.info(
            "No quotations found"
        )


    else:



        h1,h2,h3,h4,h5 = st.columns(

            [1.2,3.5,2,1.5,2]

        )


        h1.markdown("**Quote**")

        h2.markdown("**Customer**")

        h3.markdown("**Amount**")

        h4.markdown("**Status**")

        h5.markdown("**Action**")



        st.markdown(
            "<hr>",
            unsafe_allow_html=True
        )



        colors = {

            "Draft":"#64748b",

            "Sent":"#2563eb",

            "Approved":"#16a34a",

            "Rejected":"#dc2626"

        }



        for _,row in df.iterrows():



            c1,c2,c3,c4,c5 = st.columns(

                [1.2,3.5,2,1.5,2]

            )



            c1.markdown(

                f"""
                <span style="
                background:#dbeafe;
                color:#1e40af;
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
                <b style="color:#059669">
                {row['total']:,.2f}
                </b>
                """,

                unsafe_allow_html=True

            )



            status=row["status"]



            c4.markdown(

                f"""
                <span style="
                background:{colors.get(status,'#64748b')};
                color:white;
                padding:5px 12px;
                border-radius:15px;
                font-size:12px">

                {status}

                </span>
                """,

                unsafe_allow_html=True

            )



            with c5:


                b1,b2,b3 = st.columns(3)



                with b1:


                    if st.button(

                        "✏️",

                        key=f"e_{row['id']}"

                    ):


                        st.session_state.edit_id = row["id"]

                        st.session_state.edit_loaded = False

                        st.rerun()



                with b2:


                    if st.button(

                        "🗑",

                        key=f"d_{row['id']}"

                    ):


                        delete_quotation(
                            row["id"]
                        )


                        st.rerun()



                with b3:


                    safe_row = row.to_dict()


                    items = safe_row.get(
                        "items",
                        []
                    )


                    if isinstance(items,str):


                        try:

                            items=json.loads(items)

                        except:

                            items=[]



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
            
