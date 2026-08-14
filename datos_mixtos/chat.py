import os
import html
import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import streamlit as st

try:
    from dotenv import load_dotenv, find_dotenv
except ImportError:
    def find_dotenv():
        env_path = Path(__file__).resolve().parent / ".env"
        return str(env_path) if env_path.exists() else ""

    def load_dotenv(dotenv_path=None, **kwargs):
        if dotenv_path is None:
            dotenv_path = find_dotenv()
        if not dotenv_path:
            return False
        try:
            with open(dotenv_path, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    if "=" not in stripped:
                        continue
                    key, value = stripped.split("=", 1)
                    os.environ[key.strip()] = value.strip()
            return True
        except OSError:
            return False

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from sklearn.compose import ColumnTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def render_message_html(text: str) -> str:
    salida = []
    ultimo = 0
    code_pattern = re.compile(r"```[ \t]*([^\n`]*)[ \t]*\n([\s\S]*?)```")
    found_code = False

    for match in code_pattern.finditer(text):
        found_code = True
        salida.append(html.escape(text[ultimo:match.start()]).replace("\n", "<br>"))
        lenguaje = match.group(1).strip()
        codigo = match.group(2).rstrip("\n")
        codigo_html = html.escape(codigo)
        codigo_html = re.sub(r'(^\s*#.*$)', r'<span class="code-comment">\1</span>', codigo_html, flags=re.MULTILINE)
        etiqueta = (
            f'<div class="code-block-header">Código ({html.escape(lenguaje)})</div>'
            if lenguaje
            else '<div class="code-block-header">Código</div>'
        )
        salida.append(
            f'<div class="code-block">{etiqueta}'
            f'<pre>{codigo_html}</pre>'
            '</div>'
        )
        ultimo = match.end()

    contenido_restante = text[ultimo:]
    if not found_code and contenido_restante.strip().startswith("#") and contenido_restante.count("\n") >= 1:
        codigo_html = html.escape(contenido_restante.strip())
        codigo_html = re.sub(r'(^\s*#.*$)', r'<span class="code-comment">\1</span>', codigo_html, flags=re.MULTILINE)
        return (
            '<div class="code-block">'
            '<div class="code-block-header">Código</div>'
            f'<pre>{codigo_html}</pre>'
            '</div>'
        )

    salida.append(html.escape(contenido_restante).replace("\n", "<br>"))
    return "".join(salida)


def obtener_contexto_proyecto(max_chars: int = 35000) -> str:
    repo_root = Path(__file__).resolve().parent.parent
    allowed_ext = {".py", ".md", ".txt", ".yml", ".yaml", ".json", ".ini"}
    lines = []
    total_chars = 0

    for path in sorted(repo_root.rglob("*")):
        if path.is_dir() or any(part in {"venv", ".git", "__pycache__"} for part in path.parts):
            continue
        if path.suffix.lower() not in allowed_ext and path.name not in {"requirements.txt", "README.md"}:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if not text.strip():
            continue

        if path.suffix.lower() in {".md", ".txt", ".json", ".yml", ".yaml"}:
            snippet = text
        else:
            snippet = "\n".join(text.splitlines()[:250])

        if len(snippet) > 12000:
            snippet = snippet[:12000] + "\n...[contenido truncado]"

        entry = f"### ARCHIVO: {path.relative_to(repo_root)}\n{snippet}\n"
        if total_chars + len(entry) > max_chars:
            remaining = max_chars - total_chars
            if remaining > 0:
                entry = entry[:remaining] + "\n...[contexto truncado]"
                lines.append(entry)
            break

        lines.append(entry)
        total_chars += len(entry)

    if not lines:
        return "No se pudo cargar el contexto del proyecto."

    return "\n".join(lines)


def mostrar_chat():
    load_dotenv(find_dotenv())
    proyecto_contexto = obtener_contexto_proyecto()

    if len(proyecto_contexto) > 1000:
        st.info("La IA está usando el repositorio actual como contexto para tus preguntas.")
    else:
        st.info("No se cargó el contexto completo del proyecto; revisa que los archivos estén disponibles.")

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

    .chat-row { display: flex; margin: 10px 0; }
    .chat-row.user { justify-content: flex-end; }
    .chat-row.assistant { justify-content: flex-start; }

    .chat-bubble {
        display: inline-block;
        max-width: 82%;
        padding: 16px 18px;
        line-height: 1.6;
        font-size: 15px;
        border-radius: 24px;
        box-shadow: 0 18px 40px rgba(29, 35, 54, 0.08);
        word-break: break-word;
    }

    .chat-bubble.user {
        background: linear-gradient(135deg, #8b5cf6 0%, #c084fc 100%);
        color: #ffffff;
        border-radius: 24px 24px 8px 24px;
        box-shadow: 0 18px 40px rgba(139, 92, 246, 0.24);
    }

    .chat-bubble.assistant {
        background: #ffffff;
        color: #111827;
        border: 1px solid rgba(167, 139, 250, 0.22);
        border-radius: 24px 24px 24px 8px;
    }

    .chat-bubble strong, .chat-bubble b {
        color: #4f46e5;
    }

    .chat-bubble pre {
        background: #ffffff;
        color: #1f1c2a;
        padding: 16px 18px;
        border-radius: 16px;
        overflow-x: auto;
        font-family: 'SFMono-Regular', Consolas, monospace;
        font-size: 11px;
        line-height: 1.55;
        white-space: pre;
        word-break: normal;
        margin: 16px 0 0;
        border: 1px solid rgba(235, 209, 231, 0.7);
        box-shadow: 0 8px 20px rgba(235, 209, 231, 0.28);
    }

    .code-block {
    margin: 18px 0 0;
    background: #e3dae7;              /* antes: #ffffff */
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #c9b3c3;         /* borde un poco más oscuro para definir el bloque */
    box-shadow: 0 10px 24px rgba(201, 179, 195, 0.35);
    overflow-x: auto;
    }

    .code-block-header {
        color: #7c5473;                   /* un morado más oscuro para que contraste con el nuevo fondo */
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 10px;
    }

    .code-block pre {
        background: transparent;
        color: #2b1f28;                   /* texto oscuro, legible sobre #e3dae7 */
        padding: 0;
        border-radius: 0;
        overflow-x: auto;
        font-family: 'SFMono-Regular', Consolas, monospace;
        font-size: 12px;
        white-space: pre-wrap;
        word-break: normal;
        margin: 0;
    }

    .code-comment {
        color: #8a6a83;                   /* comentarios un poco más suaves pero visibles */
    }

    .chat-bubble code {
        background: rgba(17, 24, 39, 0.85);
        color: #f8fafc;
        padding: 0.18rem 0.4rem;
        border-radius: 10px;
        font-size: 13px;
    }

    .chat-bubble a {
        color: #7c3aed;
        text-decoration: underline;
    }

    .stMarkdown {
        margin-bottom: 16px;
    }

    .stChatInput textarea {
        background: #f8f4ff !important;
        border: 1px solid #d8c1ff !important;
        border-radius: 18px !important;
        color: #111827 !important;
        font-size: 15px !important;
        padding: 14px !important;
    }

    div[data-testid="stChatInput"] {
        border-radius: 20px !important;
        background: #f8f4ff !important;
        border: 1px solid #d8c1ff !important;
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
    </style>
    """

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

    if OpenAI is None:
        st.error(
            "No se encontró la librería openai. Instala la dependencia e intenta de nuevo."
        )
        st.stop()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        st.error(
            "No se encontró OPENROUTER_API_KEY. Agrega un archivo .env con esa variable en la carpeta datos_mixtos."
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
    "Responde siempre en espanol. "
    "\n\n"

    "FORMATO DE RESPUESTA (OBLIGATORIO):\n"
    "- Cuando el usuario solicite codigo, responde UNICAMENTE con un bloque de codigo Markdown de Python.\n"
    "- El bloque de codigo DEBE comenzar exactamente con ```python y terminar con ```.\n"
    "- Mantén todos los saltos de linea, espacios e indentacion normales de Python.\n"
    "- NO conviertas el codigo en un solo parrafo.\n"
    "- NO reemplaces los saltos de linea por espacios.\n"
    "- NO escapes caracteres del codigo.\n"
    "- Escribe # normalmente para los comentarios, nunca como \\#.\n"
    "- Escribe _ normalmente en nombres de variables, nunca como \\_.\n"
    "- Escribe comillas, parentesis, corchetes y operadores de Python normalmente.\n"
    "- NO uses LaTeX dentro del codigo.\n"
    "- NO uses HTML.\n"
    "- NO escribas '**Codigo**', 'Codigo:' ni ningun titulo antes del bloque.\n"
    "- NO agregues explicaciones antes ni despues del bloque de codigo.\n"
    "- NO agregues texto fuera del bloque de codigo.\n"
    "- Usa comentarios (#) DENTRO del codigo para separar y explicar brevemente cada seccion cuando sea util.\n"
    "- Entrega siempre el codigo completo, funcional y listo para copiar y pegar en un archivo .py.\n"
    "- Nunca entregues codigo como texto plano fuera de un bloque de codigo.\n"
    "- Nunca conviertas una respuesta de codigo en texto enriquecido.\n"
    "\n"
    "La estructura esperada es:\n"
    "```python\n"
    "# 1. Importar librerias\n"
    "import pandas as pd\n"
    "\n"
    "# 2. Cargar datos\n"
    "df = pd.read_csv('datos.csv')\n"
    "\n"
    "# 3. Procesar datos\n"
    "print(df.head())\n"
    "```\n"
    "\n"
    "No muestres razonamiento interno ni pensamiento interno en ninguna circunstancia.\n"
    "No digas frases como 'pienso', 'creo', 'aqui esta el codigo' ni similares.\n"
    "\n"
    "Si la pregunta es ambigua y necesitas informacion adicional, responde con una sola pregunta "
    "breve en texto normal."
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


def procesar_cluster():
    df = pd.read_csv("empleados_rrhh.csv")
    df = df.copy()
    df.describe()

    plt.figure(figsize=(8, 8))
    sns.scatterplot(data=df, x='antiguedad', y='sueldo', hue='faltas_annio', palette='viridis', s=80)
    plt.title('Relación entre Antigüedad y Sueldo (color faltas al año)')
    plt.xlabel('Antigüedad (años)')
    plt.ylabel('Sueldo mensual')
    plt.grid(True)
    plt.savefig('cluster_relacion.png')

    X = df.drop(columns=['id'])
    columnas_numericas = ['sueldo', 'hijos', 'faltas_annio', 'antiguedad']
    columnas_categoricas = ['casado', 'coche', 'casa', 'sindicato', 'sexo']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), columnas_numericas),
            ('cat', OneHotEncoder(drop='first', sparse_output=False), columnas_categoricas)
        ]
    )
    X_transformed = preprocessor.fit_transform(X)
    cat_encoder = preprocessor.named_transformers_['cat']
    cat_feature_names = cat_encoder.get_feature_names_out(columnas_categoricas)
    nombres = columnas_numericas + list(cat_feature_names)

    df_transformed = pd.DataFrame(X_transformed, columns=nombres)
    df_transformed.insert(0, 'id', df['id'])
    df_transformed.to_csv('transformado.csv', index=False, encoding='utf-8')

    X_train, X_test = train_test_split(X, test_size=0.2, random_state=123)
    num_clusters = 3
    pipeline = Pipeline([
        ('pre', preprocessor),
        ('kmeans', KMeans(n_clusters=num_clusters, init='k-means++', random_state=123, n_init=10))
    ])
    pipeline.fit(X_train)

    modelo_kMeans = pipeline.named_steps['kmeans']
    X_train_transformado = preprocessor.transform(X_train)
    silhouette = silhouette_score(X_train_transformado, modelo_kMeans.labels_)

    df['cluster'] = pipeline.predict(X)
    plt.figure(figsize=(8, 8))
    sns.scatterplot(data=df, x='antiguedad', y='sueldo', hue='cluster', palette='viridis', s=90, alpha=0.8)
    plt.title('Segmentación de trabajadores')
    plt.xlabel('Antigüedad (años)')
    plt.ylabel('Sueldo ($)')
    plt.grid(True)
    plt.savefig('segmentacion_trabajadores.png')

    joblib.dump(pipeline, 'trabajadores_cluster.plk')

    nuevos_trabajadores = pd.DataFrame({
        'sueldo': [30000, 10000, 35000, 19000, 22400],
        'casado': ['Sí', 'No', 'No', 'No', 'Sí'],
        'coche': ['No', 'Sí', 'No', 'Sí', 'Sí'],
        'hijos': [1, 0, 0, 0, 1],
        'casa': ['Propia', 'Propia', 'Alquila', 'Alquila', 'Propia'],
        'sindicato': ['No', 'Sí', 'Sí', 'No', 'Sí'],
        'faltas_annio': [2, 0, 5, 3, 1],
        'antiguedad': [1, 6, 9, 7, 8],
        'sexo': ['M', 'F', 'F', 'M', 'M']
    })
    segmentos = pipeline.predict(nuevos_trabajadores)
    mapa = {0: 'si quieren corrame', 1: 'Junior', 2: 'Base'}
    for i, seg in enumerate(segmentos):
        label = mapa.get(seg, f'Cluster {seg}')
        empleado = f"Empleado {i}: (sueldo: ${nuevos_trabajadores.loc[i, 'sueldo']}) categoria: {label}"
        print(empleado)


if __name__ == '__main__':
    procesar_cluster()
