import easyocr

reader = easyocr.Reader(['es', 'en'], gpu=False)

def extract_text(image):
    results = reader.readtext(image, detail=1, paragraph=False)

    if not results:
        return ""

    # Descartar detecciones con confianza muy baja
    results = [(bbox, text, conf) for bbox, text, conf in results if conf > 0.25]

    # Ordenar por posición Y (arriba→abajo), luego X (izquierda→derecha)
    results.sort(key=lambda r: (r[0][0][1], r[0][0][0]))

    # Agrupar en líneas por proximidad vertical
    lines = []
    current_line = []
    last_y = None

    for bbox, text, conf in results:
        y_top = bbox[0][1]
        y_bot = bbox[2][1]
        height = max(y_bot - y_top, 1)
        threshold = max(height * 0.6, 12)

        if last_y is None or abs(y_top - last_y) <= threshold:
            current_line.append((bbox[0][0], text))
        else:
            current_line.sort()
            lines.append(' '.join(t for _, t in current_line))
            current_line = [(bbox[0][0], text)]
        last_y = y_top

    if current_line:
        current_line.sort()
        lines.append(' '.join(t for _, t in current_line))

    return '\n'.join(lines)