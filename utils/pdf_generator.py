from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Table
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from io import BytesIO


def generate_quotation_pdf(data):

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # ================= CUSTOM STYLES =================
    title_style = ParagraphStyle(
        "title",
        fontSize=18,
        textColor=colors.white,
        alignment=TA_LEFT,
        fontName="Helvetica-Bold"
    )

    sub_style = ParagraphStyle(
        "sub",
        fontSize=10,
        textColor=colors.white,
        alignment=TA_RIGHT
    )

    normal_bold = ParagraphStyle(
        "bold",
        fontSize=10,
        fontName="Helvetica-Bold"
    )

    elements = []

    # ================= HEADER (MODERN BAR) =================
    header = Table([
        [
            Paragraph("COMRADE CRM<br/><font size=9>Quotation System</font>", title_style),
            Paragraph(f"QUOTATION # {data.get('id', 'N/A')}", sub_style)
        ]
    ], colWidths=[300, 240])

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0B2D5B")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#0B2D5B")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 18))

    # ================= CUSTOMER INFO (CLEAN BOX) =================
    customer_table = Table([
        [
            Paragraph("<b>Bill To</b><br/>" + data.get("customer_name", ""), styles["Normal"]),
            Paragraph(
                f"Date: {data.get('date', '')}<br/>"
                f"Phone: {data.get('phone', '')}<br/>"
                f"Email: {data.get('email', '')}",
                styles["Normal"]
            )
        ]
    ], colWidths=[270, 270])

    customer_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(customer_table)
    elements.append(Spacer(1, 15))

    # ================= ITEMS TABLE =================
    table_data = [["#", "Description", "Qty", "Unit Price", "Total"]]

    items = data.get("items", [])
    subtotal = 0

    for i, it in enumerate(items, start=1):
        qty = float(it.get("qty", 0))
        price = float(it.get("price", 0))
        total = qty * price
        subtotal += total

        table_data.append([
            str(i),
            it.get("item", ""),
            str(qty),
            f"AED {price:.2f}",
            f"AED {total:.2f}"
        ])

    item_table = Table(table_data, colWidths=[30, 230, 60, 90, 90])

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),

        ("ALIGN", (2, 1), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),

        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
    ])

    # Zebra striping
    for row in range(1, len(table_data)):
        if row % 2 == 0:
            style.add("BACKGROUND", (0, row), (-1, row), colors.HexColor("#F5F7FA"))

    item_table.setStyle(style)

    elements.append(item_table)
    elements.append(Spacer(1, 18))

    # ================= SUMMARY (RIGHT ALIGNED BOX) =================
    discount = float(data.get("discount", 0))
    tax = float(data.get("tax", 0))

    discount_amt = subtotal * discount / 100
    after_discount = subtotal - discount_amt
    tax_amt = after_discount * tax / 100
    grand_total = after_discount + tax_amt

    summary = Table([
        ["Subtotal", f"AED {subtotal:.2f}"],
        [f"Discount ({discount}%)", f"- AED {discount_amt:.2f}"],
        [f"Tax ({tax}%)", f"+ AED {tax_amt:.2f}"],
        ["", ""],
        ["GRAND TOTAL", f"AED {grand_total:.2f}"]
    ], colWidths=[180, 120])

    summary.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 11),

        ("LINEABOVE", (0, -2), (-1, -2), 0.5, colors.grey),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),

        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E8EEF7")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    summary_wrap = Table([[summary]], colWidths=[540])
    summary_wrap.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
    ]))

    elements.append(summary_wrap)
    elements.append(Spacer(1, 20))

    # ================= SIGNATURE (CLEAN) =================
    sign = Table([
        ["Authorized Signature", "Customer Signature"],
        ["__________________________", "__________________________"]
    ], colWidths=[270, 270])

    sign.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
    ]))

    elements.append(sign)
    elements.append(Spacer(1, 20))

    # ================= FOOTER =================
    footer = Paragraph(
        "<font size=9 color='grey'>"
        "Thank you for your business. This quotation is system generated and does not require a signature."
        "</font>",
        styles["Normal"]
    )

    elements.append(footer)

    doc.build(elements)
    buffer.seek(0)

    return buffer
