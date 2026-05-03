import streamlit as st
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.extractor_pdf import extract_invoice_pdf
from modules.preprocess import process_image
from modules.reader import extract_text_image
from modules.corrector import correct_text
from modules.parser import parse_invoice
from modules.storage import save_invoices, load_invoices, delete_invoice, update_invoice, get_invoice
from modules.aggregator import sum_all, sum_selection

# ── Config ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Facturas OCR",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Estilos ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp { background: #0f0f0f; color: #e8e4dc; }

h1, h2, h3 { font-family: 'IBM Plex Mono', monospace !important; letter-spacing: -0.02em; }

.block-container { padding: 2rem 3rem; max-width: 1400px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #2a2a2a;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #555;
    padding: 12px 24px;
    border-bottom: 2px solid transparent;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: #e8e4dc !important;
    border-bottom: 2px solid #c8b560 !important;
    background: transparent !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 1rem 1.25rem;
}
[data-testid="metric-container"] label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #666 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px !important;
    color: #c8b560 !important;
}

/* Botones */
.stButton > button {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-radius: 2px;
    border: 1px solid #333;
    background: #1a1a1a;
    color: #aaa;
    transition: all 0.15s;
}
.stButton > button:hover {
    background: #222;
    border-color: #555;
    color: #e8e4dc;
}

/* Botón guardar (primary) */
div[data-testid="column"]:first-child .stButton > button {
    border-color: #c8b560;
    color: #c8b560;
}
div[data-testid="column"]:first-child .stButton > button:hover {
    background: #c8b560;
    color: #0f0f0f;
}

/* Expander */
.streamlit-expanderHeader {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #555 !important;
    background: #141414 !important;
    border: 1px solid #222 !important;
}
.streamlit-expanderContent {
    background: #141414 !important;
    border: 1px solid #222 !important;
    border-top: none !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 1px dashed #333;
    border-radius: 4px;
    background: #141414;
    padding: 1rem;
}

/* Dataframe / tabla */
[data-testid="stDataFrame"] {
    border: 1px solid #2a2a2a;
    border-radius: 4px;
}

/* Inputs */
.stTextInput input, .stNumberInput input {
    background: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: #e8e4dc !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 2px !important;
}

/* Multiselect */
[data-baseweb="select"] {
    background: #1a1a1a !important;
}

/* Divider */
hr { border-color: #2a2a2a; }

/* Success / error / info */
.stSuccess { background: #0f1f0f; border-left: 3px solid #3a7a3a; }
.stError   { background: #1f0f0f; border-left: 3px solid #7a3a3a; }
.stInfo    { background: #0f0f1f; border-left: 3px solid #3a3a7a; }

/* Badge status */
.badge-ok  { display:inline-block; padding:2px 8px; border-radius:2px; font-family:'IBM Plex Mono',monospace; font-size:10px; background:#0f1f0f; color:#5a9a5a; border:1px solid #2a4a2a; }
.badge-err { display:inline-block; padding:2px 8px; border-radius:2px; font-family:'IBM Plex Mono',monospace; font-size:10px; background:#1f0f0f; color:#9a5a5a; border:1px solid #4a2a2a; }

/* Pending card */
.pending-card {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #c8b560;
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.pending-card h4 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #888;
    margin: 0 0 0.75rem 0;
}
.pending-card .total-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 32px;
    color: #c8b560;
    line-height: 1;
    margin-bottom: 0.5rem;
}
.field-row {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
    font-size: 13px;
}
.field-label { color: #555; min-width: 110px; font-size:11px; font-family:'IBM Plex Mono',monospace; text-transform:uppercase; letter-spacing:0.06em; padding-top:2px; }
.field-value { color: #c8c4bc; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "pendientes" not in st.session_state:
    st.session_state.pendientes = []
if "procesados" not in st.session_state:
    st.session_state.procesados = set()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 🧾 Facturas OCR")
st.markdown("<p style='color:#555;font-size:13px;margin-top:-0.5rem'>Extracción · Revisión · Almacenamiento</p>", unsafe_allow_html=True)
st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_subir, tab_guardadas, tab_calc = st.tabs([
    "↑  Subir y revisar",
    "▦  Facturas guardadas",
    "Σ  Calculadora"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Subir y revisar
# ══════════════════════════════════════════════════════════════════════════════
with tab_subir:
    st.markdown("### Cargar documentos")

    files = st.file_uploader(
        "Arrastra o selecciona facturas",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "bmp", "tiff", "pdf"],
        label_visibility="collapsed"
    )

    if files:
        nuevos = [f for f in files if f.name not in st.session_state.procesados]

        if nuevos:
            with st.spinner(f"Extrayendo texto de {len(nuevos)} documento(s)..."):
                for file in nuevos:
                    suffix = os.path.splitext(file.name)[1].lower()
                    tmp_path = None
                    try:
                        if suffix == ".pdf":
                            text = extract_invoice_pdf(file)
                        else:
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                            tmp.write(file.read())
                            tmp.flush()
                            tmp.close()
                            tmp_path = tmp.name
                            img = process_image(tmp_path)
                            text = extract_text_image(img)

                        corrected = correct_text(text)
                        data = parse_invoice(corrected)
                        name = os.path.splitext(file.name)[0]

                        st.session_state.pendientes.append({
                            "data": data,
                            "corrected": corrected,
                            "name": name,
                            "file_name": file.name,
                            "tmp_path": tmp_path,
                            "suffix": suffix,
                        })
                        st.session_state.procesados.add(file.name)

                    except Exception as e:
                        st.error(f"Error en {file.name}: {e}")
                        if tmp_path and os.path.exists(tmp_path):
                            os.unlink(tmp_path)

    # ── Pendientes de revisión ─────────────────────────────────────────────────
    if st.session_state.pendientes:
        st.markdown(f"### Revisión — {len(st.session_state.pendientes)} documento(s) pendiente(s)")
        st.caption("Revisa los datos extraídos y decide si guardar o descartar cada factura.")

        to_remove = []

        for idx, item in enumerate(st.session_state.pendientes):
            data = item["data"]
            corrected = item["corrected"]
            total = data.get("total")

            with st.container():
                st.markdown(f"""
                <div class="pending-card">
                    <h4>{item['file_name']}</h4>
                    <div class="total-val">{f"${total:,.2f}" if total is not None else "—"}</div>
                    <div style="margin-bottom:0.75rem">
                        {'<span class="badge-ok">Total detectado</span>' if total is not None else '<span class="badge-err">Sin total</span>'}
                    </div>
                    <div class="field-row"><span class="field-label">Proveedor</span><span class="field-value">{data.get('proveedor', '—')}</span></div>
                    <div class="field-row"><span class="field-label">Fecha</span><span class="field-value">{data.get('fecha', '—')}</span></div>
                    <div class="field-row"><span class="field-label">No. Factura</span><span class="field-value">{data.get('numero_factura', '—')}</span></div>
                    <div class="field-row"><span class="field-label">RFC</span><span class="field-value">{data.get('rfc', '—')}</span></div>
                    <div class="field-row"><span class="field-label">Folio</span><span class="field-value">{data.get('folio', '—')}</span></div>
                </div>
                """, unsafe_allow_html=True)

                if total is None:
                    total_manual = st.number_input(
                        "Ingresar total manualmente",
                        min_value=0.0, step=0.01,
                        key=f"total_manual_{idx}",
                        format="%.2f"
                    )
                    if total_manual > 0:
                        item["data"]["total"] = total_manual

                with st.expander("Ver texto OCR completo"):
                    debug = data.get("_debug_total_line")
                    if debug:
                        st.caption(f"Línea usada para total: `{debug}`")
                    st.text_area("", corrected, height=160, key=f"ocr_{idx}",
                                 label_visibility="collapsed")

                col_save, col_discard, col_space = st.columns([1, 1, 4])
                with col_save:
                    if st.button("↓ Guardar", key=f"save_{idx}"):
                        try:
                            save_invoices(item["data"], item["name"])
                            to_remove.append(idx)
                            if item["tmp_path"] and os.path.exists(item["tmp_path"]):
                                os.unlink(item["tmp_path"])
                            st.success(f"'{item['file_name']}' guardada.")
                        except Exception as e:
                            st.error(f"Error al guardar: {e}")

                with col_discard:
                    if st.button("✕ Descartar", key=f"discard_{idx}"):
                        to_remove.append(idx)
                        if item["tmp_path"] and os.path.exists(item["tmp_path"]):
                            os.unlink(item["tmp_path"])
                        st.info(f"'{item['file_name']}' descartada.")

                st.divider()

        for idx in sorted(to_remove, reverse=True):
            st.session_state.pendientes.pop(idx)

        if st.session_state.pendientes:
            if st.button("↓ Guardar todas las pendientes"):
                saved = 0
                for item in st.session_state.pendientes:
                    try:
                        save_invoices(item["data"], item["name"])
                        if item["tmp_path"] and os.path.exists(item["tmp_path"]):
                            os.unlink(item["tmp_path"])
                        saved += 1
                    except Exception as e:
                        st.error(f"Error guardando {item['file_name']}: {e}")
                st.session_state.pendientes.clear()
                st.success(f"{saved} factura(s) guardadas.")
                st.rerun()

    elif not files:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0;color:#333">
            <div style="font-size:48px;margin-bottom:1rem">🧾</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:0.1em;text-transform:uppercase">
                Arrastra archivos arriba para comenzar
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Facturas guardadas (CRUD)
# ══════════════════════════════════════════════════════════════════════════════
with tab_guardadas:
    facturas = load_invoices()

    if not facturas:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0;color:#333">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:0.1em;text-transform:uppercase">
                No hay facturas guardadas aún
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total documentos", len(facturas))
        with col2:
            total_g = sum_all(facturas)
            st.metric("Suma total", f"${total_g:,.2f}")
        with col3:
            con_total = sum(1 for f in facturas if isinstance(f.get("total"), (int, float)))
            st.metric("Con total detectado", f"{con_total}/{len(facturas)}")

        st.divider()
        st.markdown("### Documentos guardados")

        col_headers = st.columns([0.4, 2, 1.5, 1.2, 1.2, 0.8, 0.8])
        for col, h in zip(col_headers, ["#", "Nombre / Proveedor", "Fecha", "No. Factura", "Total", "", ""]):
            col.markdown(f"<span style='font-family:IBM Plex Mono,monospace;font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#555'>{h}</span>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:0.25rem 0;border-color:#2a2a2a'>", unsafe_allow_html=True)

        delete_idx = None

        for i, f in enumerate(facturas):
            total_str = f"${f['total']:,.2f}" if isinstance(f.get("total"), (int, float)) else "—"
            nombre = f.get("proveedor") or f.get("numero_factura") or f"Factura {i+1}"
            fecha = f.get("fecha") or "—"
            num_fac = f.get("numero_factura") or "—"

            cols = st.columns([0.4, 2, 1.5, 1.2, 1.2, 0.8, 0.8])
            cols[0].markdown(f"<span style='color:#444;font-family:IBM Plex Mono,monospace;font-size:12px'>{i+1:02d}</span>", unsafe_allow_html=True)
            cols[1].markdown(f"<span style='font-size:13px'>{nombre}</span>", unsafe_allow_html=True)
            cols[2].markdown(f"<span style='color:#888;font-size:12px;font-family:IBM Plex Mono,monospace'>{fecha}</span>", unsafe_allow_html=True)
            cols[3].markdown(f"<span style='color:#888;font-size:12px;font-family:IBM Plex Mono,monospace'>{num_fac}</span>", unsafe_allow_html=True)
            cols[4].markdown(f"<span style='color:#c8b560;font-family:IBM Plex Mono,monospace;font-size:13px'>{total_str}</span>", unsafe_allow_html=True)

            if cols[5].button("✕", key=f"del_{i}", help="Eliminar factura"):
                delete_idx = i

            if cols[6].button("✏", key=f"edit_{i}", help="Editar factura"):
                st.session_state["editing_idx"] = i
                st.rerun()

            st.markdown("<hr style='margin:0.1rem 0;border-color:#1a1a1a'>", unsafe_allow_html=True)

        if delete_idx is not None:
            try:
                delete_invoice(delete_idx)
                st.success("Factura eliminada.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")

        if "editing_idx" in st.session_state:
            idx = st.session_state["editing_idx"]
            fact = get_invoice(idx)
            if fact:
                st.markdown(f"### ✏️ Editar factura #{idx+1} ({fact.get('proveedor', '')})")
                col_edit1, col_edit2 = st.columns(2)
                new_prov  = col_edit1.text_input("Proveedor",            value=fact.get("proveedor") or "")
                new_num   = col_edit2.text_input("No. Factura",          value=fact.get("numero_factura") or "")
                new_date  = col_edit1.text_input("Fecha (dd/mm/aaaa)",   value=fact.get("fecha") or "")
                new_total = col_edit2.text_input("Total",                value=str(fact.get("total", "")))

                if st.button("💾 Guardar cambios"):
                    update_invoice(idx, {
                        "proveedor": new_prov,
                        "numero_factura": new_num,
                        "fecha": new_date,
                        "total": new_total,
                    })
                    del st.session_state["editing_idx"]
                    st.success("Factura actualizada.")
                    st.rerun()
                if st.button("Cancelar"):
                    del st.session_state["editing_idx"]
                    st.rerun()

        st.divider()
        with st.expander("⚠ Zona de peligro"):
            st.warning("Esta acción elimina todas las facturas guardadas y no se puede deshacer.")
            if st.button("Eliminar todas las facturas"):
                try:
                    for i in range(len(facturas) - 1, -1, -1):
                        delete_invoice(i)
                    st.success("Todas las facturas eliminadas.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Calculadora
# ══════════════════════════════════════════════════════════════════════════════
with tab_calc:
    facturas = load_invoices()

    if not facturas:
        st.info("Guarda facturas primero para poder sumarlas.")
    else:
        st.markdown("### Selecciona facturas para sumar")

        opciones = []
        for i, f in enumerate(facturas):
            nombre = f.get("proveedor") or f.get("numero_factura") or f"Factura {i+1}"
            total_str = f"${f['total']:,.2f}" if isinstance(f.get("total"), (int, float)) else "sin total"
            opciones.append(f"{i+1:02d} · {nombre} — {total_str}")

        seleccion = st.multiselect(
            "Facturas",
            options=list(range(len(facturas))),
            format_func=lambda i: opciones[i],
            label_visibility="collapsed"
        )

        st.divider()

        col_sub, col_all = st.columns(2)
        with col_sub:
            if seleccion:
                subtotal = sum_selection(facturas, seleccion)
                st.metric(label=f"Subtotal — {len(seleccion)} factura(s)", value=f"${subtotal:,.2f}")
            else:
                st.metric("Subtotal", "—")

        with col_all:
            total_global = sum_all(facturas)
            st.metric(label=f"Total global — {len(facturas)} factura(s)", value=f"${total_global:,.2f}")

        if seleccion:
            st.divider()
            st.markdown("#### Detalle de selección")
            for i in seleccion:
                f = facturas[i]
                nombre = f.get("proveedor") or f.get("numero_factura") or f"Factura {i+1}"
                total_val = f.get("total")
                total_str = f"${total_val:,.2f}" if isinstance(total_val, (int, float)) else "—"
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1a1a1a'>"
                    f"<span style='color:#888;font-size:13px'>{nombre}</span>"
                    f"<span style='font-family:IBM Plex Mono,monospace;color:#c8b560;font-size:13px'>{total_str}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
