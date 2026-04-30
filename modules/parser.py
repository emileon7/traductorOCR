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
        value = value.replace('.', '')
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
    m = re.search(r'(?:Proveedor|Emisor|Empresa|De)\s*[:\-]?\s*(.+)', t, re.IGNORECASE)
    if m:
        data['proveedor'] = m.group(1).strip()

    # Fecha
    m = re.search(
        r'(?:Fecha|Date)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        t, re.IGNORECASE
    )
    if m:
        data['fecha'] = m.group(1).strip()

    # RFC
    m = re.search(r'RFC\s*[:\-]?\s*([A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3})', t, re.IGNORECASE)
    if m:
        data['rfc'] = m.group(1).strip()

    # Total — buscar etiqueta explícita primero
    _money = r'\$?\s*([\d]{1,3}(?:[,\.]\d{3})*[,\.]\d{2}|\d+[,\.]\d{2})'
    m = re.search(
        r'(?:Total\s*(?:a\s*pagar)?|Importe\s*Total|Monto\s*Total|Gran\s*Total|TOTAL)\s*[:\-]?\s*' + _money,
        t, re.IGNORECASE
    )
    if m:
        try:
            data['total'] = _parse_money(m.group(1))
        except ValueError:
            data['total'] = None
    else:
        # Fallback: tomar el mayor monto numérico del documento
        amounts = re.findall(r'\$?\s*([\d]{1,3}(?:[,\.]\d{3})+[,\.]\d{2}|\d{4,}[,\.]\d{2})', t)
        parsed = []
        for a in amounts:
            try:
                parsed.append(_parse_money(a))
            except ValueError:
                pass
        data['total'] = max(parsed) if parsed else None

    return data