import os
import io
import contextlib
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

try:
    from dotenv import load_dotenv, find_dotenv
except ImportError:
    def find_dotenv(filename=".env"):
        start = Path(__file__).resolve()
        for base in [start.parent, *start.parents]:
            candidate = base / filename
            if candidate.exists():
                return str(candidate)
        return ""

    def load_dotenv(dotenv_path=None, **kwargs):
        env_path = dotenv_path or find_dotenv()
        if not env_path:
            return False
        try:
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#") or "=" not in stripped:
                        continue
                    key, value = stripped.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
            return True
        except OSError:
            return False

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

for env_path in [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parents[1] / ".env",
    Path.cwd() / ".env",
]:
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv(find_dotenv())


def get_openrouter_api_key():
    value = os.getenv("OPENROUTER_API_KEY")
    if value and value.strip():
        return value.strip().strip('"').strip("'")
    return None


API_KEY = get_openrouter_api_key()
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

# -------------------------------------------------
# MASCOTA (nube flotante del estado vacío del chat)
# -------------------------------------------------

MASCOTA_HTML = """
<style>
@keyframes float-bob {
    0%   { transform: translateY(0px); }
    50%  { transform: translateY(-12px); }
    100% { transform: translateY(0px); }
}
.mascota-nube-wrap {
    display: flex;
    justify-content: center;
    margin: 0.5rem 0 2rem 0;
}
.mascota-nube-wrap svg {
    width: 150px;
    height: auto;
    animation: float-bob 3s ease-in-out infinite;
}
</style>
<div class="mascota-nube-wrap">
<svg viewBox="0 0 300 220" xmlns="http://www.w3.org/2000/svg">
    <path transform="translate(8,10)"
        d="M60,120 C60,95 80,75 105,75 C110,55 130,40 155,40 C185,40 210,60 215,85
           C240,85 260,105 260,130 C260,155 240,175 215,175 L85,175
           C65,175 50,158 50,138 C50,128 54,122 60,120 Z"
        fill="#B78FB1"/>
    <path
        d="M60,120 C60,95 80,75 105,75 C110,55 130,40 155,40 C185,40 210,60 215,85
           C240,85 260,105 260,130 C260,155 240,175 215,175 L85,175
           C65,175 50,158 50,138 C50,128 54,122 60,120 Z"
        fill="#F8E6F4" stroke="#B78FB1" stroke-width="6" stroke-linejoin="round"/>
    <circle cx="135" cy="120" r="7" fill="#7A4F74"/>
    <circle cx="175" cy="120" r="7" fill="#7A4F74"/>
    <path d="M140,145 Q157,158 174,145" stroke="#7A4F74" stroke-width="5" fill="none" stroke-linecap="round"/>
</svg>
</div>
"""

# -------------------------------------------------
# ESTILOS DEL CHAT (título y botón de ejecutar)
# -------------------------------------------------

ESTILOS_CHAT = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600&display=swap');

.titulo-chat-principal {
    font-family: 'Baloo 2', cursive;
    color: #9a6f94;
    text-align: center;
    font-size: 1.7rem;
    margin: 0.2rem 0 1rem 0;
}

button[kind="primary"] {
    background-color: #B78FB1 !important;
    border-color: #B78FB1 !important;
    color: #ffffff !important;
}
button[kind="primary"]:hover {
    background-color: #9a6f94 !important;
    border-color: #9a6f94 !important;
    color: #ffffff !important;
}
button[kind="primary"]:focus:not(:active) {
    box-shadow: 0 0 0 0.15rem rgba(183, 143, 177, 0.5) !important;
}
</style>
"""

SYSTEM_PROMPT = """
Eres un experto en Python y análisis de datos.

Tu respuesta SIEMPRE debe ser ÚNICAMENTE un bloque de código Python entre
```python y ```. No escribas NADA fuera de ese bloque: ni introducción, ni
explicación, ni resumen final, ni Markdown adicional, ni la palabra "Aquí
tienes el código".

REGLAS:
- El código debe estar completo y funcionar directamente con exec().
- Explica lo necesario DENTRO del código usando comentarios #.
- No uses plt.show().
- Las gráficas deben crearse con matplotlib o seaborn.
- Si generas una tabla, guárdala en una variable llamada `resultado`.
- Si generas una gráfica, deja la figura creada para que Streamlit pueda mostrarla.
- Si no hay datos proporcionados, crea datos de ejemplo con pandas/numpy.
- No inventes resultados: calcúlalos mediante Python.
- Puedes usar pandas, numpy, matplotlib, seaborn y scikit-learn.
- No uses input(), exec(), eval(), os, subprocess ni requests.
- Cumple exactamente lo que pide el usuario.

FORMATO DE RESPUESTA (obligatorio, sin excepciones, verificado automáticamente):
```python
# tu código aquí
```

Si no sigues este formato EXACTO tu respuesta será rechazada.
"""


def get_client():
    api_key = get_openrouter_api_key()
    if not api_key:
        raise ValueError(
            "No se encontró una API key válida para OpenRouter. Revisa tu .env y usa la clave real 'sk-or-v1-...'"
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Proyecto Final",
        },
    )


def _llamar_modelo(client, mensajes):
    respuesta = client.chat.completions.create(
        model=MODEL,
        messages=mensajes,
        temperature=0,
        max_tokens=2000,
    )
    texto = respuesta.choices[0].message.content or ""
    uso = {}
    if getattr(respuesta, "usage", None):
        uso = {
            "input_tokens": getattr(respuesta.usage, "prompt_tokens", 0),
            "output_tokens": getattr(respuesta.usage, "completion_tokens", 0),
        }
    return texto, uso


def preguntar_ia(client, pregunta):
    """Envía la pregunta del usuario a OpenRouter, valida que la respuesta
    contenga código Python válido y, si no, reintenta hasta 2 veces pidiendo
    que corrija el formato. Devuelve (codigo, metricas_de_uso, error,
    ultima_respuesta_cruda)."""

    mensajes = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": pregunta},
    ]

    ultimo_texto = ""
    uso_total = {}
    intentos_max = 3  # 1 intento inicial + 2 reintentos

    for intento in range(intentos_max):
        try:
            texto, uso = _llamar_modelo(client, mensajes)
        except Exception as e:
            return None, uso_total, f"Error al comunicarse con OpenRouter: {e}", ultimo_texto

        ultimo_texto = texto
        uso_total = uso or uso_total
        codigo = extraer_codigo(texto)

        if es_python_valido(codigo):
            return codigo, uso_total, None, ultimo_texto

        # No fue válido: preparamos un reintento más estricto
        mensajes.append({"role": "assistant", "content": texto})
        mensajes.append(
            {
                "role": "user",
                "content": (
                    "Tu respuesta anterior NO cumplió el formato exigido "
                    "(debe ser únicamente un bloque ```python ... ``` con "
                    "código Python válido, sin ningún texto antes ni "
                    "después). Corrígelo y responde de nuevo cumpliendo el "
                    "formato exactamente."
                ),
            }
        )

    return None, uso_total, (
        "El modelo no devolvió código Python válido después de varios "
        "intentos. Revisa la respuesta cruda más abajo para ver qué está "
        "contestando, o prueba con otro modelo en OPENROUTER_MODEL (por "
        "ejemplo openai/gpt-4o u otro con mejor seguimiento de "
        "instrucciones)."
    ), ultimo_texto


def extraer_codigo(respuesta):
    """Extrae el bloque de código, tolerando texto extra fuera de los
    backticks, backticks sin especificar lenguaje, o la ausencia total de
    backticks."""
    if not respuesta:
        return ""

    texto = respuesta.strip()

    if "```python" in texto:
        return texto.split("```python", 1)[1].split("```", 1)[0].strip()

    if "```py" in texto:
        return texto.split("```py", 1)[1].split("```", 1)[0].strip()

    if "```" in texto:
        partes = texto.split("```")
        if len(partes) >= 2:
            # Toma el primer bloque entre backticks, sin importar el idioma indicado
            bloque = partes[1]
            # Si la primera línea es solo una etiqueta de lenguaje (ej. "python"), la quitamos
            lineas = bloque.split("\n", 1)
            if len(lineas) > 1 and lineas[0].strip().isalpha():
                bloque = lineas[1]
            return bloque.strip()

    # Sin backticks: devolvemos el texto tal cual, la validación decidirá si sirve
    return texto


def es_python_valido(codigo):
    if not codigo or not codigo.strip():
        return False
    try:
        compile(codigo, "<generado>", "exec")
        return True
    except SyntaxError:
        return False


def ejecutar_codigo(codigo):
    """Ejecuta el código generado con acceso a pandas, numpy, matplotlib
    y seaborn. Devuelve (salida_texto, resultado, figura, error)."""

    entorno = {
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
    }

    plt.close("all")
    buffer = io.StringIO()

    try:
        with contextlib.redirect_stdout(buffer):
            exec(codigo, entorno)

        salida_texto = buffer.getvalue()
        resultado = entorno.get("resultado")
        figura = plt.gcf() if plt.get_fignums() else None

        return salida_texto, resultado, figura, None

    except Exception as e:
        return buffer.getvalue(), None, None, str(e)


def mostrar_chat():
    st.markdown(ESTILOS_CHAT, unsafe_allow_html=True)
    st.markdown(
        '<div class="titulo-chat-principal">Holaaa, dame tus instrucciones</div>',
        unsafe_allow_html=True,
    )

    # Historial acumulativo del chat: cada elemento es un turno completo
    # (pregunta + código + resultados de su propia ejecución). Nunca se
    # sobrescribe, solo se le van agregando turnos nuevos.
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if not API_KEY:
        st.error(
            "No se encontró OPENROUTER_API_KEY en tu archivo .env. "
            "Agrega OPENROUTER_API_KEY=sk-or-v1-... y reinicia la app."
        )
        return

    if OpenAI is None:
        st.error(
            "No está instalado el paquete 'openai' (cliente usado para hablar con OpenRouter). "
            "Instálalo con: pip install openai"
        )
        return

    client = get_client()

    # Mascota flotante: solo se muestra en el estado vacío, antes de la primera pregunta
    if not st.session_state["chat_history"]:
        st.markdown(MASCOTA_HTML, unsafe_allow_html=True)

    # -------------------- NUEVA PREGUNTA --------------------
    # st.chat_input queda anclado en la parte inferior de la pantalla,
    # con el botón de enviar integrado en el mismo recuadro.

    pregunta = st.chat_input(
        placeholder="Ejemplo: crea un heatmap de correlación con las columnas numéricas",
        key="chat_pregunta",
    )

    if pregunta and pregunta.strip():
        with st.spinner("Generando código..."):
            codigo, metrica, error, respuesta_cruda = preguntar_ia(client, pregunta)

        # Se agrega un turno nuevo al historial; los turnos anteriores no se tocan.
        st.session_state["chat_history"].append(
            {
                "pregunta": pregunta,
                "codigo": codigo,
                "error": error,
                "respuesta_cruda": respuesta_cruda,
                "metrica": metrica,  # se guarda por si se necesita internamente, no se muestra
                "ejecutado": False,
                "salida": None,
                "resultado": None,
                "figura": None,
                "error_ejecucion": None,
            }
        )

    # -------------------- HISTORIAL COMPLETO --------------------
    # Se recorre todo el historial en cada recarga, así que las preguntas y
    # respuestas anteriores nunca desaparecen.

    for idx, turno in enumerate(st.session_state["chat_history"]):
        with st.chat_message("user", avatar="👤"):
            st.write(turno["pregunta"])

        with st.chat_message("assistant", avatar="☁️"):
            if turno["error"]:
                st.error(turno["error"])
                if turno.get("respuesta_cruda"):
                    with st.expander("Ver respuesta cruda del modelo (depuración)"):
                        st.text(turno["respuesta_cruda"])
                continue

            st.code(turno["codigo"], language="python")

            ejecutar = st.button(
                "▶ Ejecutar código", type="primary", key=f"chat_ejecutar_btn_{idx}"
            )

            if ejecutar:
                with st.spinner("Ejecutando..."):
                    salida, resultado, figura, error_ejecucion = ejecutar_codigo(turno["codigo"])

                turno["ejecutado"] = True
                turno["salida"] = salida
                turno["resultado"] = resultado
                turno["figura"] = figura
                turno["error_ejecucion"] = error_ejecucion

            if turno["error_ejecucion"]:
                st.error(f"Error al ejecutar el código: {turno['error_ejecucion']}")
                continue

            if turno["salida"]:
                st.subheader("Salida de consola")
                st.text(turno["salida"])

            if turno["resultado"] is not None:
                st.subheader("Resultado")
                if isinstance(turno["resultado"], (pd.DataFrame, pd.Series)):
                    st.dataframe(turno["resultado"], use_container_width=True)
                else:
                    st.write(turno["resultado"])

            if turno["figura"] is not None:
                st.subheader("Gráfica")
                st.pyplot(turno["figura"])

            if (
                turno["ejecutado"]
                and not turno["salida"]
                and turno["resultado"] is None
                and turno["figura"] is None
            ):
                st.info("El código se ejecutó correctamente, pero no generó texto, tabla ni gráfica para mostrar.")


if __name__ == "__main__":
    mostrar_chat()