import os
import io
import contextlib
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib

from dotenv import load_dotenv
from anthropic import Anthropic


# =========================================================
# CONFIGURACIÓN
# =========================================================
# NOTA: NO llamamos a st.set_page_config() aquí, porque
# app_principal.py ya lo hace una sola vez para toda la app.
# Llamarlo dos veces provoca un error de Streamlit.

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

API_KEY = os.getenv("ANTHROPIC_API_KEY")


# =========================================================
# PROMPT DEL SISTEMA
# =========================================================

SYSTEM_PROMPT = """
Eres un experto en programación con Python y análisis de datos.

Responde EXCLUSIVAMENTE sobre programación, especialmente Python, pandas, numpy,
matplotlib, seaborn, joblib y análisis de DataFrames.

Cuando el usuario pida código:

1. Entrega directamente código Python funcional.
2. NO uses Markdown ni bloques ```python.
3. NO escribas explicaciones fuera del código.
4. NO muestres pensamientos, razonamientos internos ni procesos internos.
5. Explica el código mediante comentarios usando #.
6. Cada línea o bloque importante del código debe tener un comentario breve que explique qué hace.
7. Usa la variable df cuando trabajes con el DataFrame del usuario.
8. Nunca inventes nombres de columnas. Si necesitas conocerlas, usa df.columns.
9. Respeta exactamente lo que pidió el usuario.
10. No agregues código innecesario.
11. Si el usuario pide una gráfica, genera directamente el código para crearla.
12. El código debe ser ejecutable y utilizar únicamente las librerías necesarias.

FORMATO DE RESPUESTA:

# Explicación breve de lo que hace esta línea o bloque
código

# Explicación breve de lo que hace esta línea o bloque
código

Solo responde con comentarios y código Python. No agregues texto fuera del código.
"""


# =========================================================
# FUNCIÓN PARA PREGUNTAR A CLAUDE
# =========================================================

def preguntar_claude(client, pregunta, contexto=""):

    mensaje = f"""
CONTEXTO DEL DATAFRAME:

{contexto}

PETICIÓN DEL USUARIO:

{pregunta}

Recuerda seguir estrictamente las instrucciones del sistema.
"""

    try:

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=4000,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": mensaje
                }
            ]
        )

        return response.content[0].text

    except Exception as e:

        return f"Error al comunicarse con Claude: {e}"


# =========================================================
# EJECUTAR CÓDIGO GENERADO
# =========================================================

def ejecutar_codigo(codigo, df):

    entorno = {
        "df": df,
        "pd": pd,
        "plt": plt,
        "joblib": joblib
    }

    salida = io.StringIO()

    try:

        with contextlib.redirect_stdout(salida):

            exec(codigo, entorno)

        resultado = salida.getvalue()

        return resultado, None

    except Exception as e:

        return None, str(e)


# =========================================================
# INTERFAZ (encapsulada para ser llamada desde app_principal.py)
# =========================================================

def mostrar_chat():

    st.title("📊 Asistente de Análisis de Datos")

    st.write(
        "Carga un archivo CSV y realiza análisis utilizando lenguaje natural."
    )

    if not API_KEY:
        st.error(
            "No se encontró ANTHROPIC_API_KEY en el archivo .env "
            "(revisa que el archivo .env esté en la misma carpeta que chat.py)."
        )
        return

    client = Anthropic(api_key=API_KEY)

    # -------------------------------------------------
    # CARGAR CSV
    # -------------------------------------------------

    archivo = st.file_uploader(
        "Selecciona un archivo CSV",
        type=["csv"],
        key="chat_csv_uploader"
    )

    if archivo is None:
        st.info("Carga un archivo CSV para comenzar.")
        return

    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        return

    st.success("Archivo cargado correctamente.")

    # -------------------------------------------------
    # INFORMACIÓN DEL DATAFRAME
    # -------------------------------------------------

    st.subheader("Vista de los datos")
    st.dataframe(df, use_container_width=True)

    with st.expander("Información del DataFrame"):

        st.write("Filas:", df.shape[0])
        st.write("Columnas:", df.shape[1])
        st.write("Columnas disponibles:")
        st.write(list(df.columns))
        st.write("Tipos de datos:")
        st.dataframe(
            pd.DataFrame(
                {
                    "Columna": df.columns,
                    "Tipo": df.dtypes.astype(str)
                }
            )
        )

    # -------------------------------------------------
    # CONTEXTO PARA CLAUDE
    # -------------------------------------------------

    contexto = f"""
Número de filas: {df.shape[0]}

Número de columnas: {df.shape[1]}

Columnas disponibles:
{list(df.columns)}

Tipos de datos:
{df.dtypes.to_string()}

Primeras filas:
{df.head(5).to_string()}

Columnas numéricas:
{list(df.select_dtypes(include="number").columns)}

Columnas categóricas:
{list(df.select_dtypes(exclude="number").columns)}
"""

    # -------------------------------------------------
    # PREGUNTA
    # -------------------------------------------------

    st.subheader("¿Qué quieres hacer?")

    pregunta = st.text_area(
        "Escribe tu instrucción:",
        placeholder=(
            "Ejemplo: crea una gráfica de tipo boxplot "
            "con las columnas numéricas"
        ),
        height=120,
        key="chat_pregunta"
    )

    # -------------------------------------------------
    # BOTÓN
    # -------------------------------------------------

    if st.button("Analizar", type="primary", key="chat_analizar_btn"):

        if not pregunta.strip():
            st.warning("Escribe una instrucción.")
        else:
            with st.spinner("Claude está generando el código..."):
                respuesta = preguntar_claude(client, pregunta, contexto)

            codigo = None
            if "```python" in respuesta:
                partes = respuesta.split("```python")
                if len(partes) > 1:
                    codigo = partes[1].split("```")[0].strip()

            # Guardamos en session_state para que sobreviva al rerun
            # que provoca el botón "Ejecutar código".
            st.session_state["chat_codigo"] = codigo
            st.session_state["chat_resultado"] = None
            st.session_state["chat_error"] = None

    # -------------------------------------------------
    # MOSTRAR CÓDIGO + BOTÓN DE EJECUTAR + RESULTADO
    # -------------------------------------------------

    codigo = st.session_state.get("chat_codigo")

    if not codigo:
        return

    st.subheader("Código generado")
    st.code(codigo, language="python")

    if st.button("Ejecutar código", key="chat_ejecutar_btn"):

        with st.spinner("Ejecutando..."):
            salida, error = ejecutar_codigo(codigo, df)

        st.session_state["chat_resultado"] = salida
        st.session_state["chat_error"] = error
        st.session_state["chat_figura"] = plt.gcf() if plt.get_fignums() else None

        if plt.get_fignums():
            plt.close("all")

    # -------------------------------------------------
    # RESULTADO (persiste tras el rerun del botón)
    # -------------------------------------------------

    if st.session_state.get("chat_error"):
        st.error(f"Error al ejecutar el código: {st.session_state['chat_error']}")
        return

    if st.session_state.get("chat_resultado"):
        st.subheader("Resultado")
        st.text(st.session_state["chat_resultado"])

    if st.session_state.get("chat_figura") is not None:
        st.subheader("Gráfica")
        st.pyplot(st.session_state["chat_figura"])