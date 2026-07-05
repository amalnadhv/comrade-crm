from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import date


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
    elements = []

    # ================= HEADER =================
    header = Table([
        ["COMRADE CRM", f"QUOTATION #{data.get('id', 'N/A')}"]
    ])

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B2D5B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 14),
        ("PADDING", (0, 0), (-1, -1), 12),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 15))

    # ================= CUSTOMER BOX =================
    customer = Table([
        ["Bill To:", data.get("customer_name", "")]
    ])

    customer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(customer)
    elements.append(Spacer(1, 15))

    # ================= ITEMS =================
    table_data = [["#", "Item", "Qty", "Price", "Total"]]

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
            f"{qty}",
            f"AED {price:.2f}",
            f"AED {total:.2f}"
        ])

    table = Table(table_data, colWidths=[30, 200, 50, 80, 80])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (2, 1), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))

    # ================= SUMMARY BOX =================
    discount = float(data.get("discount", 0))
    tax = float(data.get("tax", 0))

    after_discount = subtotal - (subtotal * discount / 100)
    grand_total = after_discount + (after_discount * tax / 100)

    summary = Table([
        ["Subtotal", f"AED {subtotal:.2f}"],
        [f"Discount ({discount}%)", f"- AED {(subtotal * discount / 100):.2f}"],
        [f"Tax ({tax}%)", f"+ AED {(after_discount * tax / 100):.2f}"],
        ["GRAND TOTAL", f"AED {grand_total:.2f}"]
    ])

    summary.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D9E1F2")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary)
    elements.append(Spacer(1, 20))

    # ================= SIGNATURE =================
    sign = Table([
        ["Approved By", "Agreed By"],
        ["__________________", "__________________"]
    ])

    sign.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 20),
    ]))

    elements.append(sign)
    elements.append(Spacer(1, 20))

    # ================= FOOTER =================
    footer = Paragraph(
        "Thank you for your business. This is a system-generated quotation.",
        styles["Italic"]
    )

    elements.append(footer)

    doc.build(elements)
    buffer.seek(0)

    return buffer
