import pdfplumber

with pdfplumber.open("data/EmilyLeonVuelo.pdf") as pdf:
    page = pdf.pages[0]

    text = page.extract_text()

    table = page.extract_table()

    print(text)