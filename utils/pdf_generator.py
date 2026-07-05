from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def generate_quotation_pdf(data):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    elements = []

    # ================= HEADER =================
    elements.append(Paragraph("<b>COMRADE CRM</b>", styles["Title"]))
    elements.append(Paragraph("QUOTATION / ESTIMATE", styles["Title"]))
    elements.append(Spacer(1, 12))

    # ================= CUSTOMER INFO =================
    customer_block = f"""
    <b>Customer:</b> {data.get('customer_name', '')} <br/>
    """
    elements.append(Paragraph(customer_block, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # ================= ITEMS TABLE =================
    table_data = [["Item", "Qty", "Price", "Total"]]

    items = data.get("items", [])
    subtotal = 0

    for it in items:
        qty = float(it.get("qty", 0))
        price = float(it.get("price", 0))
        total = qty * price
        subtotal += total

        table_data.append([
            str(it.get("item", "")),
            str(qty),
            f"{price:.2f}",
            f"{total:.2f}"
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))

    # ================= SUMMARY =================
    discount = float(data.get("discount", 0))
    tax = float(data.get("tax", 0))

    after_discount = subtotal - (subtotal * discount / 100)
    grand_total = after_discount + (after_discount * tax / 100)

    summary = f"""
    <b>Subtotal:</b> {subtotal:.2f} <br/>
    <b>Discount:</b> {discount:.2f}% <br/>
    <b>Tax:</b> {tax:.2f}% <br/>
    <b>Grand Total:</b> {grand_total:.2f}
    """

    elements.append(Paragraph(summary, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # ================= SIGNATURE BLOCK =================
    signature_table = Table([
        ["Approved By", "Agreed By"],
        ["__________________", "__________________"]
    ])

    signature_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
    ]))

    elements.append(signature_table)
    elements.append(Spacer(1, 20))

    # ================= FOOTER =================
    elements.append(Paragraph("Thank you for your business!", styles["Italic"]))

    doc.build(elements)
    buffer.seek(0)

    return buffer
