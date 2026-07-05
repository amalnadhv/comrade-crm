from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_quotation_pdf(filename, data):

    c = canvas.Canvas(filename, pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "QUOTATION")

    c.setFont("Helvetica", 12)

    y = 750

    for key, value in data.items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 25

    c.save()
