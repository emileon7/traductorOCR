import re

# Caracteres que EasyOCR confunde dentro de contextos numéricos
_OCR_NUM_MAP = {'O': '0', 'o': '0', 'D': '0', 'I': '1', 'l': '1',
                'i': '1', 'S': '5', 'B': '8', 'G': '6', 'Z': '2', 'T': '7'}

def _fix_number(m):
    """Corrige caracteres OCR dentro de secuencias numéricas."""
    s = m.group()
    return ''.join(_OCR_NUM_MAP.get(c, c) if not c.isdigit() and c not in '.,$' else c for c in s)

def correct_text(text):
    lines = text.split('\n')
    corrected = []

    for line in lines:
        # Eliminar caracteres de control y no imprimibles
        line = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', line)
        # Normalizar espacios múltiples
        line = re.sub(r'\s+', ' ', line).strip()
        if not line:
            continue

        # Corregir confusiones de caracteres en cantidades de dinero:
        # Busca patrones tipo "$1,234.56" o "1.234,56" o "118000"
        line = re.sub(r'[\$]?\s*[0-9OoIlSBGZDT]{1,3}(?:[.,][0-9OoIlSBGZDT]{2,3})+', _fix_number, line)

        corrected.append(line)

    return '\n'.join(corrected)