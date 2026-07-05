from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def generate_quotation_pdf(data):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(Paragraph("QUOTATION", styles["Title"]))
    elements.append(Spacer(1, 15))

    # Customer
    elements.append(
        Paragraph(f"<b>Customer:</b> {data.get('customer_name', '')}", styles["Normal"])
    )
    elements.append(Spacer(1, 15))

    # Table
    table_data = [["Item", "Qty", "Price", "Total"]]

    items = data.get("items", [])

    subtotal = 0

    for item in items:

        qty = float(item.get("qty", 0))
        price = float(item.get("price", 0))
        total = qty * price

        subtotal += total

        table_data.append([
            str(item.get("item", "")),
            qty,
            f"{price:.2f}",
            f"{total:.2f}"
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 15))

    discount = float(data.get("discount", 0))
    tax = float(data.get("tax", 0))
    total = float(data.get("total", subtotal))

    summary = Paragraph(
        f"""
        <b>Subtotal:</b> {subtotal:.2f}<br/>
        <b>Discount:</b> {discount:.2f}%<br/>
        <b>Tax:</b> {tax:.2f}%<br/>
        <b>Grand Total:</b> {total:.2f}
        """,
        styles["Normal"],
    )

    elements.append(summary)

    doc.build(elements)

    buffer.seek(0)

    return buffer
