import re

def _parse_money(value: str) -> float:
    """Convierte una cadena de dinero a float manejando formatos MX/EU."""
    value = value.strip().replace(' ', '').lstrip('$')
    dot_count = value.count('.')
    comma_count = value.count(',')

    if comma_count == 1 and dot_count == 0:
        # "1234,56" → separador decimal es la coma
        value = value.replace(',', '.')
    elif dot_count > 1 and comma_count == 0:
        # "1.234.567" → puntos son miles, sin decimal
        value = value.replace(',', '')
    elif comma_count > 1 and dot_count == 0:
        # "1,234,567" → comas son miles
        value = value.replace(',', '')
    elif dot_count == 1 and comma_count == 1:
        if value.index(',') < value.index('.'):
            # "1,234.56" → formato EU
            value = value.replace(',', '')
        else:
            # "1.234,56" → formato MX/EU europeo
            value = value.replace('.', '').replace(',', '.')
    else:
        value = value.replace(',', '')

    return float(value)


def parse_invoice(text: str) -> dict:
    data = {}
    t = text.replace('\r\n', '\n').replace('\r', '\n')

    # Número de factura
    m = re.search(
        r'(?:Factura|Folio|No(?:\.|º)?|Comprobante)\s*[:\-#]?\s*([\w]{2,}-?[\w]+)',
        t, re.IGNORECASE
    )
    if m:
        data['numero_factura'] = m.group(1).strip()

    # Proveedor / Emisor
    m = re.search(r'(?:Proveedor|Emisor|Empresa|De|Sucursal|Razon Social)\s*[:\-]?\s*(.+)', t, re.IGNORECASE)
    if m:
        data['proveedor'] = m.group(1).strip()

    # Fecha — formato normal dd/mm/aaaa o ISO aaaa-mm-ddThh:mm:ss (CFDIs)
    m = re.search(
        r'(?:Fecha[^:\n]*|Date)\s*[:\-]?\s*'
        r'(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?'   # ISO: 2026-04-30T15:20:28
        r'|\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',      # normal: 30/04/2026
        t, re.IGNORECASE
    )
    if m:
        data['fecha'] = m.group(1).strip()

    # RFC
    m = re.search(r'RFC\s*[:\-]?\s*([A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3})', t, re.IGNORECASE)
    if m:
        data['rfc'] = m.group(1).strip()

    # Detectar el total línea por línea.
    # Patrón de dinero: captura números con separadores de miles y decimales.
    # Ejemplos válidos: 1,180.00 | 1.180,00 | 180.00 | 1180.00
    _money_re = re.compile(
        r'\$?\s*'
        r'(\d{1,3}(?:[,\.]\d{3})+[,\.]\d{2}'   # con miles: 1,180.00 o 1.180,00
        r'|\d+[,\.]\d{2})'                       # sin miles:  180.00 o 180,00
    )
    # \bTotal\b respeta bordes de palabra: NO casa con "Subtotal"
    _total_re = re.compile(r'(?<![A-Za-z])Total(?![A-Za-z])', re.IGNORECASE)

    data['total'] = None
    data['_debug_total_line'] = None

    for line in t.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Saltar líneas que son claramente subtotales o descuentos
        if re.search(r'sub\s*total|descuento|iva|propina|cargo', line, re.IGNORECASE):
            if not _total_re.search(line):  # "IVA Total" sí tiene Total → no saltar
                continue
        if not _total_re.search(line):
            continue
        # Sacar TODOS los montos de la línea y tomar el último (el total suele ir a la derecha)
        amounts = _money_re.findall(line)
        for raw in reversed(amounts):
            try:
                data['total'] = _parse_money(raw)
                data['_debug_total_line'] = line
                break
            except ValueError:
                continue
        if data['total'] is not None:
            break

    return data