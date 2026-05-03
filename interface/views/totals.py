import streamlit as st

from modules.storage import load_invoices
from modules.aggregator import sum_all, sum_selection


def render_totals():
    st.header("Calculadora de totales")

    facturas = load_invoices()

    if not facturas:
        st.info("Sube facturas para ver los totales aquí.")
        return

    total_global = sum_all(facturas)
    st.metric(
        label=f"Total de todas las facturas ({len(facturas)} documentos)",
        value=f"${total_global:,.2f}"
    )

    st.subheader("Facturas guardadas")
    for i, f in enumerate(facturas):
        total_str = f"${f['total']:,.2f}" if isinstance(f.get("total"), (int, float)) else "Sin total"
        nombre = f.get("numero_factura") or f.get("proveedor") or f"Factura {i + 1}"
        st.write(f"**{i}.** {nombre} — {total_str}")

    st.subheader("Suma parcial")
    indices = st.multiselect(
        "Selecciona las facturas que quieres sumar",
        options=list(range(len(facturas))),
        format_func=lambda i: (
            f"{i} · "
            + (facturas[i].get("numero_factura") or facturas[i].get("proveedor") or f"Factura {i + 1}")
            + (f" — ${facturas[i]['total']:,.2f}" if isinstance(facturas[i].get("total"), (int, float)) else " — Sin total")
        )
    )

    if indices:
        subtotal = sum_selection(facturas, indices)
        st.metric(label=f"Subtotal ({len(indices)} facturas seleccionadas)", value=f"${subtotal:,.2f}")
