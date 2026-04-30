from modules.preprocess import process_image
from modules.ocr import extract_text
from modules.parser import parse_invoice
from modules.aggregator import sum_selection

path = "assets/factura_gema.png"

image = process_image(path)
text = extract_text(image)

print("=== TEXTO OCR ===")
print(text)

data = parse_invoice(text)

print("\n=== DATOS EXTRAÍDOS ===")
print(data)

facturas = [data]

#total = calcular_total(facturas)

print("\n=== TOTAL GENERAL ===")
#print(total)