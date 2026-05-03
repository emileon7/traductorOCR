import io

try:
    import pdfplumber
    _BACKEND = "pdfplumber"
except ImportError:
    try:
        import fitz  # pymupdf
        _BACKEND = "pymupdf"
    except ImportError:
        _BACKEND = None


def extract_invoice_pdf(file) -> str:
    """Extrae texto de un PDF subido desde Streamlit (UploadedFile o file-like)."""
    raw = file.read() if hasattr(file, "read") else file

    if _BACKEND == "pdfplumber":
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()

    if _BACKEND == "pymupdf":
        doc = fitz.open(stream=raw, filetype="pdf")
        pages = [doc.load_page(i).get_text() for i in range(doc.page_count)]
        return "\n".join(pages).strip()

    raise ImportError(
        "Se necesita pdfplumber o pymupdf para leer PDFs.\n"
        "Instala uno con:  pip install pdfplumber   o   pip install pymupdf"
    )
