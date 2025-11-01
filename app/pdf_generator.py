# app/pdf_generator.py
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.config import PDF_OUTPUT_DIR
from app.logger import logger

os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

def generate_quote_pdf(quote_id, data):
    path = os.path.join(PDF_OUTPUT_DIR, f"quote_{quote_id}.pdf")
    c = canvas.Canvas(path, pagesize=letter)
    t = c.beginText(40, 720)
    t.setFont("Helvetica", 12)
    t.textLine("Aura Insurance - Quotation")
    t.textLine(f"Quote ID: {quote_id}")
    for k in ("client_name", "employee_count", "insurance_type", "premium", "created_at"):
        if k in data:
            t.textLine(f"{k}: {data[k]}")
    c.drawText(t)
    c.showPage()
    c.save()
    logger.info(f"PDF generated: {path}")
    return path
