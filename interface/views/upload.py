import streamlit as st
import tempfile
import os

from modules.preprocess import process_image
from modules.ocr import extract_text
from modules.parser import parse_invoice
from modules.corrector import correct_text
from modules.storage import save_invoices


def render_upload():
    st.header("Subir facturas")
    files = st.file_uploader(
        "Arrastra o selecciona imágenes de facturas (PNG, JPG)",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "bmp", "tiff"]
    )

    if not files:
        return

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
