import os
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv(find_dotenv())

st.set_page_config(
    page_title="Asistente de Análisis de Datos",
    layout="centered"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f3f4ec;
}

#MainMenu, header, footer { visibility: hidden; }

.ai-label {
    text-align: center;
    color: #9C6C94;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.ai-greeting {
    text-align: center;
    font-size: 26px;
    font-weight: 600;
    color: #3A2E38;
    line-height: 1.4;
    margin-bottom: 4px;
}

.ai-greeting .accent { color: #B78FB1; }

@keyframes nubo-float {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-12px) scale(1.05); }
}

.nubo-wrap {
    display: flex;
    justify-content: center;
    margin: 8px 0 28px 0;
}

.nubo-cloud {
    animation: nubo-float 3.4s ease-in-out infinite;
    transform-origin: center bottom;
}

div[data-testid="column"] div.stButton > button {
    background: #f3e1ef;
    border: 1px solid #e3c9dc;
    border-radius: 6px;
    padding: 16px 14px;
    height: auto;
    min-height: 76px;
    width: 100%;
    text-align: left;
    color: #3A2E38;
    font-weight: 500;
    white-space: pre-wrap;
    line-height: 1.4;
}

div[data-testid="column"] div.stButton > button:hover {
    border: 1px solid #B78FB1;
    color: #3A2E38;
}

div[data-testid="stChatInput"] {
    border-radius: 8px !important;
    background: transparent !important;
    border: 1px solid #d9b8d1 !important;
}

div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #3A2E38 !important;
}

div[data-testid="stBottom"],
div[data-testid="stBottom"] > div,
div[data-testid="stBottomBlockContainer"],
div[data-testid="stChatInputContainer"],
div[data-testid="stChatFloatingInputContainer"] {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

div[data-testid="stBottom"]::before,
div[data-testid="stBottom"]::after {
    display: none !important;
    background: transparent !important;
}

.chat-row { display: flex; margin: 4px 0; }
.chat-row.user { justify-content: flex-end; }
.chat-row.assistant { justify-content: flex-start; }

.chat-bubble {
    display: inline-block;
    width: fit-content;
    max-width: 75%;
    padding: 10px 16px;
    line-height: 1.5;
    font-size: 15px;
}

.chat-bubble.user {
    background: #B78FB1;
    color: #ffffff;
    border-radius: 14px 14px 2px 14px;
}

.chat-bubble.assistant {
    background: #f3e1ef;
    color: #3A2E38;
    border: 1px solid #e3c9dc;
    border-radius: 14px 14px 14px 2px;
}

.chat-bubble pre {
    background: #1e1e1e;
    color: #eaeaea;
    padding: 10px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: 'SFMono-Regular', Consolas, monospace;
    font-size: 13px;
    white-space: pre;
    margin: 6px 0;
}
</style>
"""

import html
import re


def render_message_html(text: str) -> str:
    partes = re.split(r"(```[\s\S]*?```)", text)
    salida = []
    for parte in partes:
        if parte.startswith("```") and parte.endswith("```"):
            cuerpo = parte.strip("`")
            lineas = cuerpo.split("\n", 1)
            if len(lineas) > 1 and lineas[0].strip().isalpha():
                cuerpo = lineas[1]
            cuerpo = cuerpo.strip("\n")
            salida.append(f"<pre>{html.escape(cuerpo)}</pre>")
        else:
            salida.append(html.escape(parte).replace("\n", "<br>"))
    return "".join(salida)

def normalizar_codigo(codigo: str) -> str:
    """Si el código viene sin saltos de línea reales, intenta reformatearlo
    poniendo cada comentario y cada sentencia en su propia línea."""
    if codigo.count("\n") >= codigo.count("#"):
        # Ya trae saltos de línea razonables, no tocar
        return codigo

    # Poner cada comentario '#' en su propia línea
    codigo = re.sub(r'\s*#\s*', '\n# ', codigo).strip()

    # Separar "comentario: codigo" en dos líneas cuando aplique
    codigo = re.sub(r'(#[^\n]*?):\s+', r'\1\n', codigo)

    # Separar sentencias pegadas tipo ") variable = " -> ")\nvariable ="
    codigo = re.sub(r'(\))\s+(?=[a-zA-Z_][a-zA-Z0-9_]*\s*=)', r'\1\n', codigo)

    return codigo.strip()

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown('<div class="ai-label">Asistente de análisis de datos</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ai-greeting">Hola, <span class="accent">humano</span><br>'
    'dame tus instrucciones de pandas o joblib</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="nubo-wrap">
      <svg class="nubo-cloud" width="140" height="123" viewBox="0 0 260 230">
        <path d="M60 170 C30 170 10 148 10 122 C10 98 28 78 52 76 C56 48 80 26 110 26 C136 26 158 42 166 66 C192 66 214 88 214 114 C214 122 212 130 208 136 C220 142 228 154 228 168 C228 190 210 208 188 208 L72 208 C50 208 32 190 32 168 Z" fill="#f3e1ef" stroke="#B78FB1" stroke-width="2"/>
        <path d="M60 170 C40 170 24 154 24 134 C24 116 38 100 56 98 C60 74 80 56 104 56 C126 56 144 70 150 90 C170 90 186 106 186 126 C186 132 184 138 181 143 C191 148 197 158 197 168 C197 186 183 200 165 200 L74 200 C56 200 42 186 42 168 Z" fill="#f3f4ec"/>
        <ellipse cx="90" cy="140" rx="8" ry="10" fill="#9C6C94"/>
        <ellipse cx="150" cy="140" rx="8" ry="10" fill="#9C6C94"/>
        <path d="M95 165 Q120 185 145 165" fill="none" stroke="#9C6C94" stroke-width="6" stroke-linecap="round"/>
      </svg>
    </div>
    """,
    unsafe_allow_html=True,
)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    st.error(
        "No se encontró OPENROUTER_API_KEY. "
        "Agrega un archivo .env con esa variable en la carpeta datos_mixtos."
    )
    st.stop()

cliente = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

SYSTEM_PROMPT = (
    "Eres un experto analista de datos especializado unicamente en Python, pandas y joblib. "
    "Tu unica funcion es recibir instrucciones del usuario sobre analisis de datos, manipulacion "
    "de DataFrames con pandas, y serializacion/carga de modelos u objetos con joblib, y responder "
    "generando codigo o explicaciones tecnicas sobre esos temas exclusivamente. "
    "No respondas preguntas fuera de este dominio (cocina, viajes, entretenimiento, temas generales, etc.). "
    "Si el usuario pregunta algo que no esta relacionado con Python, pandas o joblib, responde brevemente "
    "que solo puedes ayudar con analisis de datos en pandas y joblib, y no generes contenido de esos otros temas. "
    "Responde siempre en espanol. Si el usuario solicita codigo, genera solo el codigo sin ejecutarlo."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

sugerencias = [
    ("Cargar datos", "Como leo un archivo CSV grande de forma eficiente con pandas"),
    ("Limpieza", "Como elimino filas duplicadas y valores nulos en un DataFrame"),
    ("Guardar modelo", "Como guardo y cargo un modelo entrenado usando joblib"),
    ("Agrupar datos", "Como hago un groupby con multiples agregaciones en pandas"),
]

if not st.session_state.chat_history:
    cols = st.columns(2)
    for i, (titulo, texto) in enumerate(sugerencias):
        with cols[i % 2]:
            if st.button(f"{titulo}\n{texto}", key=f"sugerencia_{i}"):
                st.session_state.pending_prompt = texto

pregunta = st.chat_input("Escribe tu instruccion de pandas o joblib")

if st.session_state.pending_prompt:
    pregunta = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if pregunta:
    st.session_state.chat_history.append({"role": "user", "content": pregunta})

    try:
        with st.spinner("Consultando la IA..."):
            respuesta = cliente.chat.completions.create(
                model="openrouter/auto-beta",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": pregunta},
                ],
                max_tokens=600,
                temperature=0.3,
            )

        choice = respuesta.choices[0]
        respuesta_ia = getattr(choice.message, "content", None)
        if not respuesta_ia:
            respuesta_ia = getattr(choice.message, "reasoning", None)
        if not respuesta_ia:
            respuesta_ia = "La IA respondio sin texto de salida."

        st.session_state.chat_history.append({"role": "assistant", "content": respuesta_ia})
    except Exception as e:
        st.error("Ocurrio un error al conectar con la IA:")
        st.exception(e)

if st.session_state.chat_history:
    filas_html = []
    for message in st.session_state.chat_history:
        rol = message["role"]
        contenido_html = render_message_html(message["content"])
        filas_html.append(
            f'<div class="chat-row {rol}">'
            f'<div class="chat-bubble {rol}">{contenido_html}</div>'
            f"</div>"
        )
    st.markdown("".join(filas_html), unsafe_allow_html=True)