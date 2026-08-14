import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import traceback
import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Template

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Herramienta de Análisis CSV</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --morado:     #B78FB1;
            --morado-osc: #9a6f94;
            --morado-cl:  #f2e9f1;
            --gris-f:   #1e293b;
            --gris-s:   #64748b;
            --borde:    #e2e8f0;
            --fondo:    #f8fafc;
            --blanco:   #ffffff;
            --verde:    #10b981;
            --naranja:  #f59e0b;
            --rojo:     #ef4444;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background: var(--fondo);
            font-family: 'Segoe UI', system-ui, sans-serif;
            color: var(--gris-f);
            min-height: 100vh;
        }

        .summary-pills {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 1.8rem;
            margin-top: 1rem;
        }
        .pill {
            background: var(--blanco);
            border: 1.5px solid var(--borde);
            border-radius: 50px;
            padding: .45rem 1.2rem;
            font-size: .85rem;
            font-weight: 600;
            color: var(--gris-s);
            display: flex;
            align-items: center;
            gap: .4rem;
            box-shadow: 0 2px 8px rgba(183,143,177,.12);
        }
        .pill span.badge-num {
            background: var(--morado);
            color: #fff;
            border-radius: 50px;
            padding: .15rem .55rem;
            font-size: .78rem;
        }

        .tab-nav {
            display: flex;
            gap: .5rem;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 1.5rem;
        }
        .tab-btn {
            background: var(--blanco);
            border: 1.5px solid var(--borde);
            border-radius: 50px;
            padding: .5rem 1.3rem;
            font-size: .88rem;
            font-weight: 600;
            color: var(--gris-s);
            cursor: pointer;
            transition: all .18s;
            display: flex;
            align-items: center;
            gap: .4rem;
        }
        .tab-btn:hover {
            border-color: var(--morado);
            color: var(--morado-osc);
            background: var(--morado-cl);
        }
        .tab-btn.active {
            background: var(--morado);
            color: #fff;
            border-color: var(--morado);
            box-shadow: 0 4px 12px rgba(183,143,177,.35);
        }

        .panel { display: none; }
        .panel.active { display: block; }

        .content-card {
            background: var(--blanco);
            border-radius: 14px;
            box-shadow: 0 2px 16px rgba(0,0,0,.06);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .content-card h4 {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: var(--gris-f);
            display: flex;
            align-items: center;
            gap: .5rem;
        }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .stat-card {
            background: var(--fondo);
            border: 1.5px solid var(--borde);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }
        .stat-card:hover { border-color: var(--morado); }
        .stat-card .stat-label {
            font-size: .75rem;
            text-transform: uppercase;
            letter-spacing: .05em;
            color: var(--gris-s);
            font-weight: 600;
            margin-bottom: .3rem;
        }
        .stat-card .stat-val {
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--morado-osc);
        }
        .stat-card .stat-col {
            font-size: .72rem;
            color: var(--gris-s);
            margin-top: .15rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .stat-selector {
            display: flex;
            gap: .5rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }
        .col-btn {
            background: var(--fondo);
            border: 1.5px solid var(--borde);
            border-radius: 8px;
            padding: .3rem .9rem;
            font-size: .8rem;
            font-weight: 600;
            cursor: pointer;
            color: var(--gris-s);
        }
        .col-btn:hover { border-color: var(--morado); color: var(--morado-osc); }
        .col-btn.active { background: var(--morado); color: #fff; border-color: var(--morado); }

        .table { font-size: .85rem; }
        .table thead th {
            background: var(--morado-cl);
            color: var(--morado-osc);
            font-weight: 700;
            border-bottom: 2px solid var(--morado);
            white-space: nowrap;
        }
        .table-striped > tbody > tr:nth-of-type(odd) > * {
            background-color: #f8fafc;
        }
        .table td, .table th { padding: .55rem .8rem; vertical-align: middle; }

        .chart-img {
            width: 100%;
            border-radius: 10px;
            border: 1.5px solid var(--borde);
        }

        .nulo-alto { color: var(--rojo); font-weight: 700; }
        .nulo-medio { color: var(--naranja); font-weight: 600; }
        .nulo-ok { color: var(--verde); }

        .container-main {
            max-width: 960px;
            margin: 0 auto;
            padding: 0 1rem 3rem;
        }
    </style>
</head>
<body>

<div class="container-main">

    <div class="summary-pills">
        <div class="pill"> Archivo cargado</div>
        <div class="pill">Filas <span class="badge-num">{{ resultado.filas }}</span></div>
        <div class="pill">Columnas <span class="badge-num">{{ resultado.columnas }}</span></div>
        {% if resultado.num_numericas > 0 %}
        <div class="pill">Numéricas <span class="badge-num">{{ resultado.num_numericas }}</span></div>
        {% endif %}
        {% if resultado.num_texto > 0 %}
        <div class="pill">Texto <span class="badge-num">{{ resultado.num_texto }}</span></div>
        {% endif %}
    </div>

    <div class="tab-nav">
        <button class="tab-btn active" onclick="showTab('estadisticas', this)">Estadísticas</button>
        <button class="tab-btn" onclick="showTab('tipos', this)">Tipos de Datos</button>
        <button class="tab-btn" onclick="showTab('nulos', this)">Valores Nulos</button>
        <button class="tab-btn" onclick="showTab('unicos', this)">Valores Únicos</button>
        {% if resultado.histograma %}
        <button class="tab-btn" onclick="showTab('distribucion', this)">Distribución</button>
        {% endif %}
        {% if resultado.heatmap %}
        <button class="tab-btn" onclick="showTab('heatmap', this)">Mapa de Calor</button>
        {% endif %}
    </div>

    <div id="panel-estadisticas" class="panel active">
        {% if resultado.num_numericas > 0 %}
        <div class="content-card">
            <h4>📐 Selecciona una columna numérica</h4>
            <div class="stat-selector" id="col-selector">
                {% for col in resultado.columnas_num %}
                <button class="col-btn {% if loop.first %}active{% endif %}"
                        onclick="selectCol(this, '{{ col }}')" data-col="{{ col }}">
                    {{ col }}
                </button>
                {% endfor %}
            </div>

            {% for col, stats in resultado.stats_por_col.items() %}
            <div class="stat-col-block" id="stats-{{ loop.index0 }}" data-col="{{ col }}"
                 style="display:{% if loop.first %}block{% else %}none{% endif %}">
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-label">Mínimo</div>
                        <div class="stat-val">{{ stats.min }}</div>
                        <div class="stat-col">{{ col }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Máximo</div>
                        <div class="stat-val">{{ stats.max }}</div>
                        <div class="stat-col">{{ col }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Media</div>
                        <div class="stat-val">{{ stats.media }}</div>
                        <div class="stat-col">{{ col }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Mediana</div>
                        <div class="stat-val">{{ stats.mediana }}</div>
                        <div class="stat-col">{{ col }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Desv. Est.</div>
                        <div class="stat-val">{{ stats.std }}</div>
                        <div class="stat-col">{{ col }}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">No nulos</div>
                        <div class="stat-val">{{ stats.count }}</div>
                        <div class="stat-col">{{ col }}</div>
                    </div>
                </div>
                <h4>📊 Distribución de <em>{{ col }}</em></h4>
                <img class="chart-img" src="data:image/png;base64,{{ stats.hist_img }}" alt="Histograma {{ col }}">
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="content-card">
            <p style="text-align:center; color:var(--gris-s); padding:2rem 0;">No hay columnas numéricas en este archivo.</p>
        </div>
        {% endif %}
    </div>

    <div id="panel-tipos" class="panel">
        <div class="content-card">
            <h4>Tipos de Dato por Columna</h4>
            {{ resultado.tipos|safe }}
        </div>
        {% if resultado.grafico_tipos %}
        <div class="content-card">
            <h4>Distribución de Tipos de Dato</h4>
            <img class="chart-img" src="data:image/png;base64,{{ resultado.grafico_tipos }}" alt="Tipos">
        </div>
        {% endif %}
    </div>

    <div id="panel-nulos" class="panel">
        <div class="content-card">
            <h4>Valores Nulos por Columna</h4>
            <p class="text-muted mb-3" style="font-size:.83rem;">
                Las celdas en rojo indican más del 20 % de nulos; amarillo entre 1–20 %.
            </p>
            {{ resultado.nulos_html|safe }}
        </div>
    </div>

    <div id="panel-unicos" class="panel">
        <div class="content-card">
            <h4>Valores Únicos por Columna</h4>
            {{ resultado.unicos|safe }}
        </div>
    </div>

    {% if resultado.histograma %}
    <div id="panel-distribucion" class="panel">
        <div class="content-card">
            <h4>Gráfica de Distribución — primera columna numérica</h4>
            <img class="chart-img" src="data:image/png;base64,{{ resultado.histograma }}" alt="Distribución">
        </div>
    </div>
    {% endif %}

    {% if resultado.heatmap %}
    <div id="panel-heatmap" class="panel">
        <div class="content-card">
            <h4>Mapa de Calor — Correlación entre columnas numéricas</h4>
            <img class="chart-img" src="data:image/png;base64,{{ resultado.heatmap }}" alt="Heatmap">
        </div>
    </div>
    {% endif %}

</div>

<script>
function showTab(name, btn) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    var panel = document.getElementById('panel-' + name);
    if (panel) panel.classList.add('active');
    btn.classList.add('active');
}

function selectCol(btn, colName) {
    document.querySelectorAll('.col-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.stat-col-block').forEach(b => b.style.display = 'none');
    var block = document.querySelector('.stat-col-block[data-col="' + CSS.escape(colName) + '"]');
    if (block) block.style.display = 'block';
}
</script>

</body>
</html>
"""


def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return encoded


def procesar_csv(df):
    resultado = {}
    resultado["filas"] = df.shape[0]
    resultado["columnas"] = df.shape[1]

    tipos_df = pd.DataFrame(df.dtypes, columns=["Tipo de Dato"])
    tipos_df["Tipo de Dato"] = tipos_df["Tipo de Dato"].astype(str)
    resultado["tipos"] = tipos_df.to_html(classes="table table-striped table-hover", border=0)

    tipo_counts = tipos_df["Tipo de Dato"].value_counts()
    colors = ['#B78FB1', '#9a6f94', '#f59e0b', '#ef4444', '#8b5cf6']
    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.barh(tipo_counts.index.tolist(), tipo_counts.values,
                    color=colors[:len(tipo_counts)], edgecolor='white', height=0.5)
    ax.set_xlabel("Cantidad de columnas", fontsize=9)
    ax.set_title("Tipos de dato en el dataset", fontsize=11, fontweight='bold', pad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for bar, val in zip(bars, tipo_counts.values):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', fontsize=9, fontweight='600')
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')
    resultado["grafico_tipos"] = fig_to_b64(fig)

    nulos_serie = df.isnull().sum()
    nulos_pct = (nulos_serie / len(df) * 100).round(1)
    nulos_df = pd.DataFrame({"Valores Nulos": nulos_serie, "% Nulos": nulos_pct})

    def color_nulos(row):
        pct = row["% Nulos"]
        if pct > 20:
            return ['color:#ef4444;font-weight:700'] * 2
        elif pct > 0:
            return ['color:#f59e0b;font-weight:600'] * 2
        return ['color:#10b981'] * 2

    resultado["nulos_html"] = nulos_df.style \
        .apply(color_nulos, axis=1) \
        .format({"% Nulos": "{:.1f}%"}) \
        .set_table_attributes('class="table table-striped table-hover"') \
        .to_html()

    resultado["unicos"] = pd.DataFrame(
        df.nunique(), columns=["Valores Únicos"]
    ).to_html(classes="table table-striped table-hover", border=0)

    numericas = df.select_dtypes(include=np.number)
    resultado["num_numericas"] = len(numericas.columns)
    resultado["num_texto"] = len(df.select_dtypes(exclude=np.number).columns)
    resultado["columnas_num"] = list(numericas.columns)

    resultado["stats_por_col"] = {}
    resultado["histograma"] = ""
    resultado["heatmap"] = ""

    if len(numericas.columns) > 0:
        for col in numericas.columns:
            serie = numericas[col].dropna()
            stats = {
                "min": round(float(serie.min()), 4),
                "max": round(float(serie.max()), 4),
                "media": round(float(serie.mean()), 4),
                "mediana": round(float(serie.median()), 4),
                "std": round(float(serie.std()), 4),
                "count": int(serie.count()),
            }

            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.set_facecolor('#f8fafc')
            fig.patch.set_facecolor('#f8fafc')
            sns.histplot(serie, kde=True, ax=ax, color='#B78FB1', edgecolor='white', alpha=0.8)
            ax.axvline(stats["media"], color='#ef4444', linestyle='--',
                       linewidth=1.5, label=f'Media: {stats["media"]}')
            ax.axvline(stats["mediana"], color='#10b981', linestyle=':',
                       linewidth=1.5, label=f'Mediana: {stats["mediana"]}')
            ax.legend(fontsize=8)
            ax.set_title(f"Distribución de {col}", fontsize=11, fontweight='bold')
            ax.set_xlabel(col, fontsize=9)
            ax.set_ylabel("Frecuencia", fontsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            stats["hist_img"] = fig_to_b64(fig)
            resultado["stats_por_col"][col] = stats

        first_col = numericas.columns[0]
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#f8fafc')
        ax.set_facecolor('#f8fafc')
        sns.histplot(numericas[first_col], kde=True, ax=ax,
                     color='#B78FB1', edgecolor='white', alpha=0.8)
        ax.set_title(f"Distribución de {first_col}", fontsize=12, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        resultado["histograma"] = fig_to_b64(fig)

        if len(numericas.columns) > 1:
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#f8fafc')
            ax.set_facecolor('#f8fafc')
            sns.heatmap(numericas.corr(), annot=True, fmt=".2f", cmap="RdPu",
                        ax=ax, linewidths=.5, annot_kws={"size": 9})
            ax.set_title("Mapa de Calor — Correlaciones", fontsize=12, fontweight='bold', pad=12)
            resultado["heatmap"] = fig_to_b64(fig)

    return resultado


def mostrar_analisis():
    st.markdown("""
        <style>
            .titulo-csv { color: #9a6f94; text-align: center; font-weight: 800; }
            .subtitulo-csv { text-align: center; color: #7a7280; margin-top: -8px; margin-bottom: 1.2rem; }
            [data-testid="stFileUploader"] {
                border: 1.5px dashed #B78FB1;
                border-radius: 12px;
                padding: 10px;
                background-color: #faf6fa;
            }
            [data-testid="stFileUploaderDropzone"] button {
                background-color: #B78FB1 !important;
                color: white !important;
                border: none !important;
            }
            [data-testid="stFileUploaderDropzone"] button:hover {
                background-color: #9a6f94 !important;
            }
            .empty-upload-box {
                background: #ffffff;
                border-radius: 14px;
                box-shadow: 0 2px 16px rgba(0,0,0,.06);
                padding: 3rem 1rem;
                text-align: center;
                margin-top: 1rem;
            }
            .empty-upload-box .upload-icon {
                width: 64px;
                height: 64px;
                border-radius: 16px;
                background-color: #B78FB1;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1.2rem auto;
                font-size: 1.8rem;
                color: white;
            }
            .empty-upload-box p.titulo-vacio {
                font-weight: 700;
                color: #1e293b;
                font-size: 1rem;
                margin-bottom: .4rem;
            }
            .empty-upload-box p.subtitulo-vacio {
                color: #64748b;
                font-size: .85rem;
            }
        </style>
        <h1 class="titulo-csv">Herramienta de Análisis CSV</h1>
        <p class="subtitulo-csv">Carga un archivo CSV y explora sus estadísticas al instante</p>
    """, unsafe_allow_html=True)

    archivo = st.file_uploader("Selecciona tu archivo CSV", type=["csv"], key="analisis_uploader")

    resultado = None
    if archivo is not None:
        try:
            df = pd.read_csv(io.BytesIO(archivo.getvalue()))
            resultado = procesar_csv(df)
        except Exception:
            st.error("Ocurrió un error al procesar el archivo CSV:")
            st.code(traceback.format_exc())
            return
    else:
        st.markdown("""
            <div class="empty-upload-box">
                <div class="upload-icon">⬆</div>
                <p class="titulo-vacio">Sube un archivo CSV para comenzar el análisis</p>
                <p class="subtitulo-vacio">Se generarán estadísticas, gráficas y mapas de calor automáticamente</p>
            </div>
        """, unsafe_allow_html=True)

    if resultado is not None:
        template = Template(HTML)
        html_render = template.render(resultado=resultado)

        num_col = resultado.get("num_numericas", 0)
        altura = 1800 + (num_col * 550)

        components.html(html_render, height=altura, scrolling=True)