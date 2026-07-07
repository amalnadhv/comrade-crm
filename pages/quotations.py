import streamlit as st
import pandas as pd
import json
from datetime import date
import sqlite3

from database import add_quotation, get_quotations, get_customers
from utils.pdf_generator import generate_quotation_pdf

DB_NAME = "crm.db"


# ================= UPDATE =================
def update_quotation(qid, customer_name, items, subtotal, discount, tax, total, status, version):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE quotations
        SET customer_name=?, items=?, subtotal=?, discount=?, tax=?, total=?, status=?, version=?
        WHERE id=?
    """, (
        customer_name,
        json.dumps(items),
        subtotal,
        discount,
        tax,
        total,
        status,
        version,
        qid
    ))

    conn.commit()
    conn.close()


# ================= DELETE =================
def delete_quotation(qid):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM quotations WHERE id=?", (qid,))
    conn.commit()
    conn.close()


# ================= PAGE =================
def quotations_page():

    st.title("💼 Quotations")

    # session init
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

    # data
    df = get_quotations()

    customers = get_customers()
    customers = pd.DataFrame(
        customers,
        columns=["id", "name", "phone", "email", "company", "status"]
    )

    customer_map = {r.id: f"{r.name} ({r.company})" for r in customers.itertuples()}
    customer_options = list(customer_map.keys())

    # create new
    col1, col2 = st.columns(2)

    if col1.button("➕ Create New Quotation"):
        st.session_state.edit_id = None
        st.session_state.quote_items = []
        st.session_state.edit_loaded = False
        st.session_state.edit_customer = None
        st.session_state.edit_status = "Draft"
        st.rerun()

    # load edit
    if st.session_state.edit_id and not st.session_state.edit_loaded:

        match = df[df["id"] == st.session_state.edit_id]

        if not match.empty:
            row = match.iloc[0]

            try:
                st.session_state.quote_items = json.loads(row["items"])
            except:
                st.session_state.quote_items = []

            st.session_state.edit_customer = row["customer_name"]
            st.session_state.edit_status = row["status"]

        st.session_state.edit_loaded = True

    # mode
    st.subheader("🟠 Edit Quotation" if st.session_state.edit_id else "🔵 Create New Quotation")

    default_customer = customer_options[0]

    if st.session_state.edit_id:
        default_customer = next(
            (k for k, v in customer_map.items()
             if v == st.session_state.edit_customer),
            customer_options[0]
        )

    # customer
    customer_id = st.selectbox(
        "Customer",
        customer_options,
        index=customer_options.index(default_customer),
        format_func=lambda x: customer_map[x],
        key="customer_select"
    )

    # status
    status = st.selectbox(
        "Status",
        ["Draft", "Sent", "Approved", "Rejected"],
        index=(
            ["Draft", "Sent", "Approved", "Rejected"].index(st.session_state.edit_status)
            if st.session_state.edit_status in ["Draft", "Sent", "Approved", "Rejected"]
            else 0
        ),
        key="status_select"
    )

    # item input
    st.markdown("### Items")

    item_input = st.text_input("Item", key="item_input")
    qty_input = st.number_input("Qty", value=1.0, key="qty_input")
    price_input = st.number_input("Price", value=0.0, key="price_input")

    if st.button("➕ Add Item"):
        st.session_state.quote_items.append({
            "item": item_input,
            "qty": qty_input,
            "price": price_input
        })
        st.rerun()

    # item list
    subtotal = 0
    updated_items = []

    for i, it in enumerate(st.session_state.quote_items):

        cols = st.columns([3, 2, 2, 1])

        new_item = cols[0].text_input("Item", it["item"], key=f"it_{i}")
        new_qty = cols[1].number_input("Qty", value=float(it["qty"]), key=f"qt_{i}")
        new_price = cols[2].number_input("Price", value=float(it["price"]), key=f"pr_{i}")

        subtotal += new_qty * new_price

        if cols[3].button("❌", key=f"rm_{i}"):
            continue

        updated_items.append({
            "item": new_item,
            "qty": new_qty,
            "price": new_price
        })

    st.session_state.quote_items = updated_items

    st.markdown("---")

    # totals
    discount = st.number_input("Discount %", value=0.0, key="discount")
    tax = st.number_input("Tax %", value=0.0, key="tax")

    after_discount = subtotal - (subtotal * discount / 100)
    total = after_discount + (after_discount * tax / 100)

    st.success(f"Subtotal: {subtotal:.2f}")
    st.success(f"Total: {total:.2f}")

    # save
    if st.button("💾 Save Quotation"):

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

            st.success("Updated successfully!")
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

            st.success("Saved successfully!")

        st.session_state.quote_items = []
        st.rerun()

    # list
    st.markdown("---")
    st.subheader("All Quotations")

    df = get_quotations()

    for _, row in df.iterrows():

        st.markdown(f"""
        ### {row['customer_name']}
        **Total:** {row['total']} | **Status:** {row['status']}
        """)

        c1, c2, c3 = st.columns(3)

        if c1.button("✏ Edit", key=f"e_{row['id']}"):
            st.session_state.edit_id = row["id"]
            st.session_state.edit_loaded = False
            st.rerun()

        if c2.button("🗑 Delete", key=f"d_{row['id']}"):
            delete_quotation(row["id"])
            st.rerun()

        # ================= PDF FIXED =================
        safe_row = row.to_dict()

        items = safe_row.get("items", [])

        if isinstance(items, str):
            try:
                items = json.loads(items)
            except:
                items = []

        safe_row["items"] = items

        pdf_buffer = generate_quotation_pdf(safe_row)

        c3.download_button(
            label="📄 PDF",
            data=pdf_buffer,
            file_name=f"quotation_{row['id']}.pdf",
            mime="application/pdf",
            key=f"pdf_{row['id']}"
        )

        st.markdown("---")
            # =====================================================
    # QUOTATION FORM
    # =====================================================


    st.markdown("---")


    if st.session_state.quote_edit_id:


        st.subheader(
            "✏️ Edit Quotation"
        )


    else:


        st.subheader(
            "➕ Create New Quotation"
        )




    # ---------------- CUSTOMER ----------------


    default_customer = customer_ids[0]



    if st.session_state.quote_customer:


        match = [

            k for k,v in customer_map.items()

            if v == st.session_state.quote_customer

        ]


        if match:

            default_customer=match[0]



    customer_id = st.selectbox(

        "Customer",

        customer_ids,

        index=customer_ids.index(
            default_customer
        ),

        format_func=lambda x:
        customer_map[x],

        key="quotation_customer"

    )




    # ---------------- STATUS ----------------


    status_list=[

        "Draft",

        "Sent",

        "Approved",

        "Rejected"

    ]



    status=st.selectbox(

        "Quotation Status",

        status_list,

        index=status_list.index(

            st.session_state.quote_status

            if st.session_state.quote_status in status_list

            else "Draft"

        ),

        key="quotation_status"

    )




    # =====================================================
    # ITEM ENTRY
    # =====================================================


    st.markdown("### 📦 Quotation Items")



    c1,c2,c3,c4=st.columns(

        [3,1,1,1]

    )



    with c1:

        item_name=st.text_input(

            "Item",

            key="new_item"

        )


    with c2:

        qty=st.number_input(

            "Qty",

            min_value=1.0,

            value=1.0,

            key="new_qty"

        )


    with c3:

        price=st.number_input(

            "Price",

            min_value=0.0,

            value=0.0,

            key="new_price"

        )


    with c4:

        st.write("")

        st.write("")


        add_item = st.button(

            "➕",

            key="add_item"

        )



    if add_item:


        if item_name.strip():


            st.session_state.quote_items.append(

                {

                    "item":
                    item_name,

                    "qty":
                    qty,

                    "price":
                    price

                }

            )


            st.rerun()



        else:

            st.warning(
                "Item name required"
            )





    # =====================================================
    # ITEMS TABLE
    # =====================================================



    subtotal=0

    final_items=[]



    if st.session_state.quote_items:



        headers=st.columns(

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


            cols=st.columns(

                [3,1,1,1]

            )



            with cols[0]:

                new_item=st.text_input(

                    "item",

                    item["item"],

                    key=f"quote_item_{i}",

                    label_visibility="collapsed"

                )



            with cols[1]:

                new_qty=st.number_input(

                    "qty",

                    value=float(item["qty"]),

                    key=f"quote_qty_{i}",

                    label_visibility="collapsed"

                )



            with cols[2]:

                new_price=st.number_input(

                    "price",

                    value=float(item["price"]),

                    key=f"quote_price_{i}",

                    label_visibility="collapsed"

                )



            with cols[3]:


                remove=st.button(

                    "🗑",

                    key=f"remove_{i}"

                )



            if not remove:


                final_items.append(

                    {

                    "item":new_item,

                    "qty":new_qty,

                    "price":new_price

                    }

                )



            subtotal += new_qty * new_price



        st.session_state.quote_items=final_items




    # =====================================================
    # TOTALS
    # =====================================================


    st.markdown("---")



    c1,c2=st.columns(2)



    with c1:


        discount=st.number_input(

            "Discount %",

            min_value=0.0,

            key="discount"

        )



    with c2:


        tax=st.number_input(

            "Tax %",

            min_value=0.0,

            key="tax"

        )




    after_discount = (

        subtotal -

        (subtotal * discount / 100)

    )


    total = (

        after_discount +

        (after_discount * tax /100)

    )



    st.info(

        f"Subtotal : {subtotal:,.2f}"

    )


    st.success(

        f"Total : {total:,.2f}"

    )



    # =====================================================
    # SAVE LOGIC WITH DUPLICATION CONTROL
    # =====================================================


    if st.button(

        "💾 Save Quotation",

        width="stretch"

    ):



        customer_name=customer_map[customer_id]



        # duplicate check only for new quotations

        duplicate=False



        if not st.session_state.quote_edit_id:


            existing=df[

                (df.customer_name==customer_name)

                &

                (df.total==total)

                &

                (df.status==status)

            ]



            if not existing.empty:


                duplicate=True




        if duplicate:


            st.error(

                "Duplicate quotation already exists ❌"

            )



        else:



            if st.session_state.quote_edit_id:



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



                st.session_state.quote_edit_id=None



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
        "📄 All Quotations"
    )



    df = get_quotations()



    if df.empty:


        st.info(
            "No quotations found"
        )


        return




    # =====================================================
    # SEARCH
    # =====================================================


    search = st.text_input(
        "🔍 Search quotations"
    )



    if search:


        df=df[
            df.astype(str)
            .apply(
                lambda x:
                x.str.contains(
                    search,
                    case=False,
                    na=False
                )
            )
            .any(axis=1)

        ]




    # =====================================================
    # EXPORT
    # =====================================================


    csv=df.to_csv(
        index=False
    ).encode("utf-8")



    st.download_button(

        "⬇ Download Quotations",

        csv,

        "quotations.csv",

        "text/csv",

        width="stretch"

    )




    # =====================================================
    # STATUS DISPLAY
    # =====================================================


    status_badge={


        "Draft":

        """

        <span class="status-draft">

        🔵 Draft

        </span>

        """,



        "Sent":

        """

        <span class="status-sent">

        🟡 Sent

        </span>

        """,



        "Approved":

        """

        <span class="status-approved">

        🟢 Approved

        </span>

        """,



        "Rejected":

        """

        <span class="status-rejected">

        🔴 Rejected

        </span>

        """

    }





    # =====================================================
    # HEADER ROW
    # =====================================================


    headers=st.columns(

        [

            3,

            1.5,

            1.5,

            1.5,

            2

        ]

    )



    titles=[

        "👥 Customer",

        "💰 Total",

        "📅 Date",

        "Status",

        "Actions"

    ]



    for col,title in zip(headers,titles):


        col.markdown(

        f"""

        <div class="table-header">

        {title}

        </div>

        """,

        unsafe_allow_html=True

        )





    st.markdown("<br>", unsafe_allow_html=True)





    # =====================================================
    # DATA ROWS
    # =====================================================


    for row in df.itertuples():



        cols=st.columns(

            [

                3,

                1.5,

                1.5,

                1.5,

                2

            ]

        )



        with cols[0]:


            st.write(

                f"👥 {row.customer_name}"

            )



        with cols[1]:


            st.write(

                f"{row.total:,.2f}"

            )



        with cols[2]:


            st.write(

                row.created_on

            )



        with cols[3]:


            st.markdown(

                status_badge.get(

                    row.status,

                    row.status

                ),

                unsafe_allow_html=True

            )




        with cols[4]:


            b1,b2,b3 = st.columns(3)



            # EDIT

            with b1:


                if st.button(

                    "✏️",

                    key=f"edit_quote_{row.id}",

                    help="Edit quotation"

                ):


                    st.session_state.quote_edit_id=row.id

                    st.session_state.quote_loaded=False

                    st.rerun()



            # DELETE

            with b2:


                if st.button(

                    "🗑️",

                    key=f"delete_quote_{row.id}",

                    help="Delete quotation"

                ):


                    delete_quotation(

                        row.id

                    )


                    show_message(

                        "Quotation deleted 🗑️"

                    )


                    st.rerun()




            # PDF

            with b3:


                safe_row=row._asdict()



                items=safe_row.get(

                    "items",

                    []

                )



                if isinstance(items,str):


                    try:

                        items=json.loads(items)

                    except:

                        items=[]



                safe_row["items"]=items



                pdf=generate_quotation_pdf(

                    safe_row

                )



                st.download_button(

                    "📄",

                    pdf,

                    file_name=f"quotation_{row.id}.pdf",

                    mime="application/pdf",

                    key=f"pdf_{row.id}",

                    help="Download PDF"

                )




        st.markdown(

        """

        <hr style="

        margin:4px 0px;

        border:0;

        border-top:1px solid #eeeeee;

        ">

        """,

        unsafe_allow_html=True

        )
        
