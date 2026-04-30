import streamlit as st
import tempfile
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.preprocess import process_image
from modules.ocr import extract_text
from modules.parser import parse_invoice
from modules.corrector import correct_text
from modules.storage import save_invoices, load_invoices
from modules.aggregator import sum_all, sum_selection

st.set_page_config(page_title="Calculadora de Facturas OCR", page_icon="🧾", layout="wide")
st.title("🧾 Calculadora de Facturas OCR")

# ── Subir facturas ─────────────────────────────────────────────────────────────
st.header("Subir facturas")
files = st.file_uploader(
    "Arrastra o selecciona imágenes de facturas (PNG, JPG)",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg", "bmp", "tiff"]
)

if files:
    for file in files:
        suffix = os.path.splitext(file.name)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(file.read())
        tmp.flush()
        tmp.close()

        with st.expander(f"Factura: {file.name}", expanded=True):
            col_img, col_data = st.columns([1, 2])

            with st.spinner("Procesando..."):
                try:
                    img = process_image(tmp.name)
                    text = extract_text(img)
                    corrected = correct_text(text)
                    data = parse_invoice(corrected)
                    name = os.path.splitext(file.name)[0]
                    save_invoices(data, name)
                except Exception as e:
                    st.error(f"Error procesando {file.name}: {e}")
                    os.unlink(tmp.name)
                    continue

            with col_img:
                st.image(tmp.name, caption="Imagen original", use_container_width=True)

            with col_data:
                st.subheader("Texto detectado (corregido)")
                st.text_area("", corrected, height=200, key=f"txt_{file.name}")

                st.subheader("Datos extraídos")
                if data:
                    st.table([data])
                    if data.get("total") is None:
                        st.warning("No se pudo extraer el total de esta factura.")
                else:
                    st.warning("No se encontraron datos en esta factura.")

        os.unlink(tmp.name)

    st.success("Facturas procesadas y guardadas correctamente.")

# ── Calculadora de totales ─────────────────────────────────────────────────────
st.divider()
st.header("Calculadora de totales")

facturas = load_invoices()

if not facturas:
    st.info("Sube facturas para ver los totales aquí.")
else:
    # Total global — siempre visible
    total_global = sum_all(facturas)
    st.metric(
        label=f"Total de todas las facturas ({len(facturas)} documentos)",
        value=f"${total_global:,.2f}"
    )

    st.subheader("Facturas guardadas")
    for i, f in enumerate(facturas):
        total_str = f"${f['total']:,.2f}" if isinstance(f.get('total'), (int, float)) else "Sin total"
        nombre = f.get('numero_factura') or f.get('proveedor') or f"Factura {i + 1}"
        st.write(f"**{i}.** {nombre} — {total_str}")

    # Suma parcial por selección
    st.subheader("Suma parcial")
    indices = st.multiselect(
        "Selecciona las facturas que quieres sumar",
        options=list(range(len(facturas))),
        format_func=lambda i: (
            f"{i} · "
            + (facturas[i].get('numero_factura') or facturas[i].get('proveedor') or f"Factura {i + 1}")
            + f" — ${facturas[i]['total']:,.2f}" if isinstance(facturas[i].get('total'), (int, float))
            else f"{i} · Factura {i + 1} — Sin total"
        )
    )

    if indices:
        subtotal = sum_selection(facturas, indices)
        st.metric(label=f"Subtotal ({len(indices)} facturas seleccionadas)", value=f"${subtotal:,.2f}")