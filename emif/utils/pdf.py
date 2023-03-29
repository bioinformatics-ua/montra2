from xhtml2pdf import pisa

import cStringIO as StringIO

def create_pdf(pdf_data):
    pdf = StringIO.StringIO()
    pisa.CreatePDF(StringIO.StringIO(pdf_data), pdf)

    return pdf

