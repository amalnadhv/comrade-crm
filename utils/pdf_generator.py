from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def generate_quotation_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("QUOTATION", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Customer Info
    info = Paragraph(f"Customer: {data['customer_name']}", styles["Normal"])
    elements.append(info)
    elements.append(Spacer(1, 12))

    # Items Table
    table_data = [["Item", "Qty", "Price", "Total"]]

    for item in data["items"]:
        table_data.append([
            item["item"],
            item["qty"],
            item["price"],
            item["total"]
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Summary
    summary = Paragraph(
        f"Subtotal: {data['subtotal']} <br/>"
        f"Discount: {data['discount']}% <br/>"
        f"Tax: {data['tax']}% <br/>"
        f"Total: {data['total']}",
        styles["Normal"]
    )

    elements.append(summary)

    doc.build(elements)
    buffer.seek(0)

    return buffer
