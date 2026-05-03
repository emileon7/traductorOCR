import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from interface.views.upload import render_upload
from interface.views.totals import render_totals

st.set_page_config(page_title="Calculadora de Facturas OCR", page_icon="🧾", layout="wide")
st.title("🧾 Calculadora de Facturas OCR")

render_upload()
st.divider()
render_totals()
