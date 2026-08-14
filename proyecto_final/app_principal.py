import os
import sys
import streamlit as st
from analisis_csv import mostrar_analisis
from prediccion_precio_casa import mostrar_prediccion

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datos_mixtos.chat import mostrar_chat

st.set_page_config(page_title="Proyecto Final", layout="wide", initial_sidebar_state="expanded")

# =====================================================
# Estado inicial
# =====================================================
if "seccion" not in st.session_state:
    st.session_state.seccion = "analisis"
if "colapsado" not in st.session_state:
    st.session_state.colapsado = False

colapsado = st.session_state.colapsado
ancho = "80px" if colapsado else "230px"

# =====================================================
# Estilos
# =====================================================
st.markdown(f"""
    <style>
        [data-testid="collapsedControl"] {{ display: none; }}

        [data-testid="stSidebar"] > div:first-child {{
            width: {ancho} !important;
            min-width: {ancho} !important;
            background-color: #ffffff;
            border-right: 1px solid #f2e9f1;
            transition: width .2s ease;
            padding-top: 0.5rem;
        }}

        .sidebar-header {{
            display: flex;
            align-items: center;
            justify-content: {'center' if colapsado else 'space-between'};
            padding: 0.4rem 0.6rem 0.8rem 0.9rem;
        }}
        .sidebar-header .titulo {{
            font-weight: 700;
            font-size: 1.05rem;
            color: #9a6f94;
            white-space: nowrap;
            overflow: hidden;
        }}

        .st-key-toggle_sidebar button {{
            background-color: #ffffff;
            border: 1px solid #e8dfe6;
            color: #9a6f94;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            padding: 0;
            box-shadow: 0 2px 6px rgba(0,0,0,.08);
        }}
        .st-key-toggle_sidebar button:hover {{
            background-color: #f7f0f6;
            border-color: #B78FB1;
        }}

        [data-testid="stSidebar"] div.stButton button {{
            background-color: transparent;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.92rem;
            color: #6b6470;
            padding: 0.65rem 0.9rem;
            width: 100%;
            margin-bottom: 0.15rem;
            box-shadow: none;
            justify-content: {'center' if colapsado else 'flex-start'};
        }}
        [data-testid="stSidebar"] div.stButton button:hover {{
            background-color: #f7f0f6;
            color: #9a6f94;
        }}
        [data-testid="stSidebar"] div.stButton button:focus:not(:active) {{
            box-shadow: none;
        }}

        div[class*="st-key-nav_analisis"] button {{
            {'background-color:#B78FB1 !important;color:#fff !important;' if st.session_state.seccion == 'analisis' else ''}
        }}
        div[class*="st-key-nav_prediccion"] button {{
            {'background-color:#B78FB1 !important;color:#fff !important;' if st.session_state.seccion == 'prediccion' else ''}
        }}
        div[class*="st-key-nav_chat"] button {{
            {'background-color:#B78FB1 !important;color:#fff !important;' if st.session_state.seccion == 'chat' else ''}
        }}
    </style>
""", unsafe_allow_html=True)


if not colapsado:
    col_titulo, col_toggle = st.sidebar.columns([4, 1])
    with col_titulo:
        st.markdown('<div class="sidebar-header" style="padding:0;"><span class="titulo">Proyecto Final</span></div>', unsafe_allow_html=True)
    with col_toggle:
        if st.button("«", key="toggle_sidebar"):
            st.session_state.colapsado = True
            st.rerun()
else:
    if st.sidebar.button("»", key="toggle_sidebar"):
        st.session_state.colapsado = False
        st.rerun()

st.sidebar.markdown('<hr style="border-color:#f2e9f1; margin: 0.4rem 0 0.8rem 0;">', unsafe_allow_html=True)


opciones = [
    {"key": "analisis", "icono": ":material/bar_chart:", "label": "Análisis de datos"},
    {"key": "prediccion", "icono": ":material/home:", "label": "Predicción de precio"},
    {"key": "chat", "icono": ":material/chat:", "label": "Chat de análisis"},
]

for op in opciones:
    texto = "" if colapsado else op["label"]
    if st.sidebar.button(texto, icon=op["icono"], key=f"nav_{op['key']}", use_container_width=True):
        st.session_state.seccion = op["key"]
        st.rerun()

if st.session_state.seccion == "analisis":
    mostrar_analisis()
elif st.session_state.seccion == "prediccion":
    mostrar_prediccion()
elif st.session_state.seccion == "chat":
    mostrar_chat()