import pdfplumber

def extract_invoice_pdf(pdf_file_path):
    text = ""

    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            table = page.extract_table()
            for row in table:
                row_text= " ".join(cell for cell in row if cell is not None)
                text += "\n" + row_text
            else:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    return text


