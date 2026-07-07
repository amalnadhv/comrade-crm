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
# DATABASE FUNCTIONS
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

        SET customer_name=?,
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
# MESSAGE SYSTEM
# =====================================================

def show_message(msg):

    st.session_state.quote_msg = msg



def render_message():

    if st.session_state.get("quote_msg"):

        st.success(
            st.session_state.quote_msg
        )

        st.session_state.quote_msg = None



# =====================================================
# PAGE
# =====================================================

def quotations_page():


    # =================================================
    # CSS
    # =================================================


    st.markdown(
    """

    <style>


    .crm-header {

        background:
        linear-gradient(
        135deg,
        #6a11cb,
        #2575fc
        );

        padding:22px 30px;

        border-radius:15px;

        margin-bottom:20px;

        box-shadow:
        0 4px 12px rgba(0,0,0,0.15);

    }



    .crm-title {

        color:white;

        font-size:32px;

        font-weight:800;

    }



    .crm-subtitle {

        color:#eef5ff;

        font-size:15px;

        margin-top:8px;

    }



    .table-header {

        background:#2575fc;

        color:white;

        padding:8px;

        border-radius:8px;

        text-align:center;

        font-weight:bold;

    }



    .status-draft {

        background:#dbeafe;

        color:#1d4ed8;

        padding:5px 12px;

        border-radius:20px;

        font-weight:bold;

    }



    .status-sent {

        background:#fff3cd;

        color:#856404;

        padding:5px 12px;

        border-radius:20px;

        font-weight:bold;

    }



    .status-approved {

        background:#d1fae5;

        color:#047857;

        padding:5px 12px;

        border-radius:20px;

        font-weight:bold;

    }



    .status-rejected {

        background:#fee2e2;

        color:#b91c1c;

        padding:5px 12px;

        border-radius:20px;

        font-weight:bold;

    }


    </style>


    """,

    unsafe_allow_html=True

    )




    st.markdown(
    """

    <div class="crm-header">

        <div class="crm-title">

            💼 Quotations Dashboard

        </div>


        <div class="crm-subtitle">

            Create quotations, track approvals and manage customer proposals

        </div>


    </div>

    """,

    unsafe_allow_html=True

    )



    render_message()



    # =================================================
    # SESSION INITIALIZATION (FIXED)
    # =================================================


    if "quote_items" not in st.session_state:

        st.session_state.quote_items = []



    if "quote_edit_id" not in st.session_state:

        st.session_state.quote_edit_id = None



    if "quote_loaded" not in st.session_state:

        st.session_state.quote_loaded = False



    if "quote_customer" not in st.session_state:

        st.session_state.quote_customer = None



    if "quote_status" not in st.session_state:

        st.session_state.quote_status = "Draft"



    if "quote_msg" not in st.session_state:

        st.session_state.quote_msg = None



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



    customer_ids = list(customer_map.keys())



    if not customer_ids:

        st.warning(
            "Please create customers first"
        )

        return



    # =================================================
    # NEW QUOTATION
    # =================================================


    if st.button(
        "➕ New Quotation",
        width="stretch"
    ):


        st.session_state.quote_edit_id = None

        st.session_state.quote_items = []

        st.session_state.quote_loaded = False

        st.session_state.quote_customer = None

        st.session_state.quote_status = "Draft"

        st.rerun()



    # =================================================
    # LOAD EDIT DATA
    # =================================================


    if (
        st.session_state.get("quote_edit_id")
        and
        not st.session_state.get("quote_loaded")
    ):


        selected = df[
            df["id"] ==
            st.session_state.quote_edit_id
        ]


        if not selected.empty:


            row = selected.iloc[0]


            try:

                st.session_state.quote_items = json.loads(
                    row["items"]
                )

            except:

                st.session_state.quote_items = []



            st.session_state.quote_customer = row["customer_name"]

            st.session_state.quote_status = row["status"]



        st.session_state.quote_loaded = True
            # =====================================================
    # QUOTATION FORM
    # =====================================================


    st.markdown("---")


    if st.session_state.get("quote_edit_id"):

        st.subheader(
            "✏️ Edit Quotation"
        )

    else:

        st.subheader(
            "➕ Create New Quotation"
        )



    # =====================================================
    # CUSTOMER SELECTION
    # =====================================================


    default_customer = customer_ids[0]


    if st.session_state.get("quote_customer"):


        found = [

            k for k,v in customer_map.items()

            if v == st.session_state.quote_customer

        ]


        if found:

            default_customer = found[0]



    customer_id = st.selectbox(

        "Customer",

        customer_ids,

        index=customer_ids.index(
            default_customer
        ),

        format_func=lambda x:
        customer_map[x],

        key="quote_customer_select"

    )



    # =====================================================
    # STATUS
    # =====================================================


    status_list = [

        "Draft",
        "Sent",
        "Approved",
        "Rejected"

    ]


    current_status = (
        st.session_state.quote_status
        if st.session_state.quote_status in status_list
        else "Draft"
    )



    status = st.selectbox(

        "Status",

        status_list,

        index=status_list.index(
            current_status
        ),

        key="quote_status_select"

    )



    # =====================================================
    # ADD ITEM
    # =====================================================


    st.markdown(
        "### 📦 Items"
    )


    c1,c2,c3,c4 = st.columns(
        [3,1,1,1]
    )


    with c1:

        item_name = st.text_input(
            "Item",
            key="quote_new_item"
        )


    with c2:

        qty = st.number_input(
            "Qty",
            min_value=1.0,
            value=1.0,
            key="quote_new_qty"
        )


    with c3:

        price = st.number_input(
            "Price",
            min_value=0.0,
            value=0.0,
            key="quote_new_price"
        )


    with c4:

        st.write("")

        add_item = st.button(
            "➕",
            key="quote_add_item"
        )



    if add_item:


        if item_name.strip():


            st.session_state.quote_items.append(

                {

                    "item": item_name,

                    "qty": qty,

                    "price": price

                }

            )

            st.rerun()


        else:

            st.warning(
                "Item name required"
            )



    # =====================================================
    # ITEM LIST
    # =====================================================


    subtotal = 0

    new_items = []



    if st.session_state.quote_items:



        headers = st.columns(
            [3,1,1,1]
        )


        for col,title in zip(
            headers,
            [
                "Item",
                "Qty",
                "Price",
                "Remove"
            ]
        ):

            col.markdown(

                f"""

                <div class="table-header">

                {title}

                </div>

                """,

                unsafe_allow_html=True

            )



        for i,item in enumerate(
            st.session_state.quote_items
        ):


            cols = st.columns(
                [3,1,1,1]
            )



            new_item = cols[0].text_input(

                "item",

                item["item"],

                key=f"edit_item_{i}",

                label_visibility="collapsed"

            )


            new_qty = cols[1].number_input(

                "qty",

                value=float(item["qty"]),

                key=f"edit_qty_{i}",

                label_visibility="collapsed"

            )



            new_price = cols[2].number_input(

                "price",

                value=float(item["price"]),

                key=f"edit_price_{i}",

                label_visibility="collapsed"

            )



            remove = cols[3].button(

                "🗑",

                key=f"remove_item_{i}"

            )



            if not remove:


                new_items.append(

                    {

                        "item":new_item,

                        "qty":new_qty,

                        "price":new_price

                    }

                )


            subtotal += (
                new_qty *
                new_price
            )



        st.session_state.quote_items = new_items




    # =====================================================
    # TOTAL CALCULATION
    # =====================================================


    st.markdown("---")


    c1,c2 = st.columns(2)



    with c1:

        discount = st.number_input(

            "Discount %",

            min_value=0.0,

            key="quote_discount"

        )



    with c2:

        tax = st.number_input(

            "Tax %",

            min_value=0.0,

            key="quote_tax"

        )



    discounted_amount = (

        subtotal -
        (
            subtotal *
            discount /
            100
        )

    )


    total = (

        discounted_amount +

        (
            discounted_amount *
            tax /
            100
        )

    )



    st.info(

        f"Subtotal : {subtotal:,.2f}"

    )


    st.success(

        f"Total : {total:,.2f}"

    )




    # =====================================================
    # SAVE WITH DUPLICATE CHECK
    # =====================================================


    if st.button(

        "💾 Save Quotation",

        width="stretch",

        key="save_quote"

    ):



        customer_name = customer_map[
            customer_id
        ]



        duplicate = False



        # Only check duplicate for NEW

        if not st.session_state.get(
            "quote_edit_id"
        ):


            existing = df[

                (df["customer_name"] == customer_name)

                &

                (df["total"] == total)

                &

                (df["status"] == status)

            ]



            if not existing.empty:

                duplicate = True




        if duplicate:


            st.error(

                "Duplicate quotation found ❌"

            )



        else:



            if st.session_state.get(
                "quote_edit_id"
            ):



                update_quotation(

                    st.session_state.quote_edit_id,

                    customer_name,

                    st.session_state.quote_items,

                    subtotal,

                    discount,

                    tax,

                    total,

                    status,

                    "V-EDIT"

                )


                show_message(

                    "Quotation updated successfully ✅"

                )



                st.session_state.quote_edit_id = None



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


                show_message(

                    "Quotation saved successfully ✅"

                )



            st.session_state.quote_items=[]

            st.session_state.quote_loaded=False


            st.rerun()
                # =====================================================
    # QUOTATION LIST
    # =====================================================


    st.markdown("---")


    st.subheader(
        "📋 All Quotations"
    )


    df = get_quotations()



    if df is None or df.empty:


        st.info(
            "No quotations available"
        )

        return



    # =====================================================
    # SEARCH
    # =====================================================


    search = st.text_input(

        "🔍 Search quotation",

        key="quotation_search"

    )



    if search:


        df = df[

            df["customer_name"]
            .str.contains(
                search,
                case=False,
                na=False
            )

            |

            df["status"]
            .str.contains(
                search,
                case=False,
                na=False
            )

        ]



    # =====================================================
    # STATUS STYLE
    # =====================================================


    status_badge = {


        "Draft":
        "🟦 Draft",


        "Sent":
        "🟡 Sent",


        "Approved":
        "🟢 Approved",


        "Rejected":
        "🔴 Rejected"

    }




    # =====================================================
    # GRID DISPLAY
    # =====================================================


    cols_per_row = 3


    rows = [

        df.iloc[i:i+cols_per_row]

        for i in range(
            0,
            len(df),
            cols_per_row
        )

    ]




    for row_group in rows:



        cols = st.columns(
            cols_per_row
        )



        for col,row in zip(
            cols,
            row_group.itertuples()
        ):



            with col:



                with st.container(
                    border=True
                ):



                    st.markdown(

                        f"""

                        ### 💼 {row.customer_name}

                        """,

                    )



                    st.markdown(

                        f"""

                        💰 **Amount**

                        {row.total:,.2f}

                        """

                    )



                    st.markdown(

                        f"""

                        📅 Date :

                        {row.date}

                        """

                    )



                    st.markdown(

                        f"""

                        🏷️ Status :

                        {status_badge.get(
                            row.status,
                            row.status
                        )}

                        """,

                    )



                    st.markdown("---")



                    b1,b2,b3 = st.columns(3)




                    # ================= EDIT =================


                    with b1:


                        if st.button(

                            "✏️",

                            key=f"quote_edit_{row.id}",

                            help="Edit quotation"

                        ):


                            st.session_state.quote_edit_id = row.id

                            st.session_state.quote_loaded=False

                            st.rerun()





                    # ================= DELETE =================


                    with b2:


                        if st.button(

                            "🗑",

                            key=f"quote_delete_{row.id}",

                            help="Delete quotation"

                        ):



                            delete_quotation(
                                row.id
                            )


                            show_message(

                                "Quotation deleted 🗑️"

                            )


                            st.rerun()





                    # ================= PDF =================


                    with b3:


                        safe_row = row._asdict()



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

                                items=[]



                        safe_row["items"]=items



                        pdf = generate_quotation_pdf(
                            safe_row
                        )



                        st.download_button(

                            "📄",

                            data=pdf,

                            file_name=
                            f"quotation_{row.id}.pdf",

                            mime=
                            "application/pdf",

                            key=f"pdf_{row.id}"

                        )
                        
