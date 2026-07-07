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
# PAGE
# =====================================================

def quotations_page():


    # ---------------- CSS ----------------

    st.markdown(
        """
        <style>

        .quote-card {

            background:white;
            padding:20px;
            border-radius:12px;
            box-shadow:0 2px 8px rgba(0,0,0,.08);
            margin-bottom:15px;

        }


        .total-box {

            background:#f5f7fb;
            padding:18px;
            border-radius:12px;
            text-align:right;

        }


        .big-total {

            font-size:28px;
            font-weight:700;

        }


        .status-draft {

            background:#fff3cd;
            padding:5px 12px;
            border-radius:20px;

        }


        .status-approved {

            background:#d1e7dd;
            padding:5px 12px;
            border-radius:20px;

        }


        .status-sent {

            background:#cff4fc;
            padding:5px 12px;
            border-radius:20px;

        }


        .status-rejected {

            background:#f8d7da;
            padding:5px 12px;
            border-radius:20px;

        }

        </style>
        """,
        unsafe_allow_html=True
    )



    st.title("💼 Quotations")



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



    # ---------------- DATA ----------------


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

        r.id:
        f"{r.name} ({r.company})"

        for r in customers.itertuples()

    }



    customer_options = list(customer_map.keys())



    if not customer_options:

        st.warning(
            "Please create customers first."
        )

        return



    # =====================================================
    # HEADER
    # =====================================================


    col1, col2 = st.columns([3,1])


    with col1:

        if st.session_state.edit_id:

            st.subheader(
                "✏ Edit Quotation"
            )

        else:

            st.subheader(
                "➕ Create New Quotation"
            )


    with col2:

        if st.button(
            "New Quotation",
            use_container_width=True
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


        row = quotation_df[
            quotation_df["id"]
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
    # CUSTOMER SECTION
    # =====================================================


    left,right = st.columns(2)



    with left:


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



    with right:


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
            )
            if st.session_state.edit_status in status_list
            else 0,

            key="status_select"

        )



    st.divider()
        # =====================================================
    # ITEM ENTRY
    # =====================================================

    st.subheader("🛒 Quotation Items")


    item_col1, item_col2, item_col3, item_col4 = st.columns(
        [4,1.5,2,1]
    )


    with item_col1:
        item_input = st.text_input(
            "Description",
            key="item_input"
        )


    with item_col2:
        qty_input = st.number_input(
            "Qty",
            min_value=1.0,
            value=1.0,
            step=1.0,
            key="qty_input"
        )


    with item_col3:
        price_input = st.number_input(
            "Unit Price",
            min_value=0.0,
            value=0.0,
            step=0.01,
            key="price_input"
        )


    with item_col4:

        st.write("")

        if st.button(
            "➕",
            key="add_item",
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

                st.rerun()



    st.divider()



    # =====================================================
    # ITEM TABLE
    # =====================================================


    subtotal = 0

    updated_items = []


    if st.session_state.quote_items:


        header = st.columns(
            [4,1.5,2,1.5]
        )

        header[0].markdown("**Item**")
        header[1].markdown("**Qty**")
        header[2].markdown("**Price**")
        header[3].markdown("**Amount**")



        for i,item in enumerate(
            st.session_state.quote_items
        ):


            cols = st.columns(
                [4,1.5,2,1.5]
            )


            new_item = cols[0].text_input(

                "Item",

                value=item["item"],

                key=f"item_{i}",

                label_visibility="collapsed"

            )


            new_qty = cols[1].number_input(

                "Qty",

                value=float(item["qty"]),

                key=f"qty_{i}",

                label_visibility="collapsed"

            )


            new_price = cols[2].number_input(

                "Price",

                value=float(item["price"]),

                key=f"price_{i}",

                label_visibility="collapsed"

            )


            amount = (
                new_qty *
                new_price
            )


            cols[3].markdown(
                f"""
                {amount:,.2f}

                """
            )


            subtotal += amount



            remove = cols[3].button(

                "❌",

                key=f"remove_{i}"

            )


            if not remove:


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
            "No items added yet."
        )



    st.divider()



    # =====================================================
    # CALCULATION SECTION
    # =====================================================


    calc1,calc2 = st.columns(2)



    with calc1:


        discount = st.number_input(

            "Discount %",

            min_value=0.0,

            value=0.0,

            step=0.5,

            key="discount"

        )


        tax = st.number_input(

            "Tax %",

            min_value=0.0,

            value=0.0,

            step=0.5,

            key="tax"

        )



    with calc2:


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



        st.markdown(

            f"""

            <div class="total-box">

            <div>
            Subtotal :
            <b>{subtotal:,.2f}</b>
            </div>


            <div>
            Discount :
            <b>{discount}%</b>
            </div>


            <div>
            Tax :
            <b>{tax}%</b>
            </div>


            <hr>


            <div class="big-total">

            Total :
            {total:,.2f}

            </div>


            </div>

            """,

            unsafe_allow_html=True

        )



    st.divider()



    # =====================================================
    # SAVE BUTTON
    # =====================================================


    save_text = (

        "Update Quotation"
        if st.session_state.edit_id
        else
        "Save Quotation"

    )


    if st.button(

        f"💾 {save_text}",

        use_container_width=True

    ):


        customer_name = customer_map[
            customer_id
        ]



        if not st.session_state.quote_items:


            st.warning(
                "Please add at least one item."
            )

            return



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



        st.session_state.quote_items = []

        st.session_state.edit_id = None

        st.session_state.edit_loaded = False

        st.session_state.edit_customer = None

        st.session_state.edit_status = "Draft"


        st.rerun()
            # =====================================================
    # QUOTATION LIST
    # =====================================================


    st.divider()

    st.subheader("📋 All Quotations")



    quotation_df = get_quotations()



    if quotation_df.empty:


        st.info(
            "No quotations available."
        )


    else:


        # ---------------- SEARCH ----------------


        search = st.text_input(

            "🔍 Search quotation",

            placeholder="Search customer name..."

        )


        if search:


            quotation_df = quotation_df[
                quotation_df["customer_name"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]



        # ---------------- DISPLAY ----------------


        for _, row in quotation_df.iterrows():


            status_class = {

                "Draft":"status-draft",

                "Sent":"status-sent",

                "Approved":"status-approved",

                "Rejected":"status-rejected"

            }.get(

                row["status"],

                "status-draft"

            )



            st.markdown(

                f"""

                <div class="quote-card">


                <h3>
                📄 Quotation #{row['id']}
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


                <br><br>


                <span class="{status_class}">
                {row['status']}
                </span>


                </div>


                """,

                unsafe_allow_html=True

            )



            b1,b2,b3 = st.columns(3)



            # ---------------- EDIT ----------------


            with b1:


                if st.button(

                    "✏ Edit",

                    key=f"edit_{row['id']}",

                    use_container_width=True

                ):


                    st.session_state.edit_id = row["id"]

                    st.session_state.edit_loaded = False

                    st.rerun()



            # ---------------- DELETE ----------------


            with b2:


                if st.button(

                    "🗑 Delete",

                    key=f"delete_{row['id']}",

                    use_container_width=True

                ):


                    delete_quotation(
                        row["id"]
                    )

                    st.success(
                        "Deleted successfully"
                    )

                    st.rerun()



            # ---------------- PDF ----------------


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

                    label="📄 PDF",

                    data=pdf_buffer,

                    file_name=
                    f"quotation_{row['id']}.pdf",

                    mime=
                    "application/pdf",

                    key=
                    f"pdf_{row['id']}",

                    use_container_width=True

                )



            st.divider()
            
