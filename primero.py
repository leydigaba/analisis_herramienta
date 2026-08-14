from flask import Flask, request, render_template_string
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io

app = Flask(__name__)

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
            --azul:     #2563eb;
            --azul-cl:  #eff6ff;
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

        /* ── Header ── */
        .header {
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 60%, #3b82f6 100%);
            padding: 2.5rem 1rem 3.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .header::after {
            content: '';
            position: absolute;
            bottom: -2px; left: 0; right: 0;
            height: 40px;
            background: var(--fondo);
            clip-path: ellipse(55% 100% at 50% 100%);
        }
        .header h1 {
            font-size: clamp(1.6rem, 4vw, 2.4rem);
            font-weight: 800;
            color: #fff;
            letter-spacing: -0.5px;
        }
        .header p {
            color: #bfdbfe;
            margin-top: .4rem;
            font-size: .95rem;
        }

        /* ── Upload card ── */
        .upload-card {
            background: var(--blanco);
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(37,99,235,.10);
            padding: 2rem;
            max-width: 560px;
            margin: -1.5rem auto 2rem;
            position: relative;
            z-index: 10;
        }
        .upload-card .form-control {
            border: 2px dashed var(--borde);
            border-radius: 10px;
            padding: .8rem 1rem;
            transition: border-color .2s;
        }
        .upload-card .form-control:focus {
            border-color: var(--azul);
            box-shadow: none;
        }
        .btn-analizar {
            background: var(--azul);
            border: none;
            border-radius: 10px;
            color: #fff;
            font-weight: 700;
            font-size: 1rem;
            padding: .75rem 2rem;
            width: 100%;
            margin-top: .8rem;
            transition: background .2s, transform .1s;
        }
        .btn-analizar:hover { background: #1d4ed8; transform: translateY(-1px); }

        /* ── Summary pills ── */
        .summary-pills {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 1.8rem;
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
            box-shadow: 0 2px 8px rgba(0,0,0,.05);
        }
        .pill span.badge-num {
            background: var(--azul);
            color: #fff;
            border-radius: 50px;
            padding: .15rem .55rem;
            font-size: .78rem;
        }

        /* ── Tab nav ── */
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
            border-color: var(--azul);
            color: var(--azul);
            background: var(--azul-cl);
        }
        .tab-btn.active {
            background: var(--azul);
            color: #fff;
            border-color: var(--azul);
            box-shadow: 0 4px 12px rgba(37,99,235,.30);
        }

        /* ── Panels ── */
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

        /* ── Stat cards for Estadísticas ── */
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
            transition: border-color .18s;
        }
        .stat-card:hover { border-color: var(--azul); }
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
            color: var(--azul);
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
            transition: all .15s;
            color: var(--gris-s);
        }
        .col-btn:hover { border-color: var(--azul); color: var(--azul); }
        .col-btn.active { background: var(--azul); color: #fff; border-color: var(--azul); }

        /* ── Tables ── */
        .table { font-size: .85rem; }
        .table thead th {
            background: var(--azul-cl);
            color: var(--azul);
            font-weight: 700;
            border-bottom: 2px solid var(--azul);
            white-space: nowrap;
        }
        .table-striped > tbody > tr:nth-of-type(odd) > * {
            background-color: #f8fafc;
        }
        .table td, .table th { padding: .55rem .8rem; vertical-align: middle; }

        /* ── Charts ── */
        .chart-img {
            width: 100%;
            border-radius: 10px;
            border: 1.5px solid var(--borde);
        }

        /* ── Nulos badge ── */
        .nulo-alto { color: var(--rojo); font-weight: 700; }
        .nulo-medio { color: var(--naranja); font-weight: 600; }
        .nulo-ok { color: var(--verde); }

        .container-main {
            max-width: 960px;
            margin: 0 auto;
            padding: 0 1rem 3rem;
        }

        /* ── Empty state ── */
        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: var(--gris-s);
        }
        .empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }

        /* ── Alert ── */
        .alert-info-custom {
            background: var(--azul-cl);
            border: 1.5px solid #bfdbfe;
            border-radius: 10px;
            color: #1d4ed8;
            padding: .75rem 1rem;
            font-size: .85rem;
            font-weight: 500;
        }
    </style>
</head>
<body>

<div class="header">
    <h1>Herramienta de Análisis CSV</h1>
    <p>Carga un archivo CSV y explora sus estadísticas al instante</p>
</div>

<div class="container-main">

    <!-- Upload -->
    <div class="upload-card">
        <form method="POST" enctype="multipart/form-data">
            <label class="form-label fw-semibold mb-2" style="font-size:.9rem;">Selecciona tu archivo</label>
            <input type="file" class="form-control" name="archivo" accept=".csv" required>
            <button type="submit" class="btn-analizar">⚡ Analizar Archivo</button>
        </form>
    </div>

    {% if resultado %}

    <!-- Summary pills -->
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

    <!-- Tab buttons -->
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

    <!-- ═══ PANEL: Estadísticas ═══ -->
    <div id="panel-estadisticas" class="panel active">
        {% if resultado.num_numericas > 0 %}

        <!-- column selector -->
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

            <!-- stat cards per column (hidden by JS) -->
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
            <div class="empty-state">
                <div class="icon"></div>
                <p>No hay columnas numéricas en este archivo.</p>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- ═══ PANEL: Tipos de Datos ═══ -->
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

    <!-- ═══ PANEL: Valores Nulos ═══ -->
    <div id="panel-nulos" class="panel">
        <div class="content-card">
            <h4>Valores Nulos por Columna</h4>
            <p class="text-muted mb-3" style="font-size:.83rem;">
                Las celdas en rojo indican más del 20 % de nulos; amarillo entre 1–20 %.
            </p>
            {{ resultado.nulos_html|safe }}
        </div>
    </div>

    <!-- ═══ PANEL: Valores Únicos ═══ -->
    <div id="panel-unicos" class="panel">
        <div class="content-card">
            <h4>Valores Únicos por Columna</h4>
            {{ resultado.unicos|safe }}
        </div>
    </div>

    <!-- ═══ PANEL: Distribución global ═══ -->
    {% if resultado.histograma %}
    <div id="panel-distribucion" class="panel">
        <div class="content-card">
            <h4>Gráfica de Distribución — primera columna numérica</h4>
            <img class="chart-img" src="data:image/png;base64,{{ resultado.histograma }}" alt="Distribución">
        </div>
    </div>
    {% endif %}

    <!-- ═══ PANEL: Mapa de Calor ═══ -->
    {% if resultado.heatmap %}
    <div id="panel-heatmap" class="panel">
        <div class="content-card">
            <h4>Mapa de Calor — Correlación entre columnas numéricas</h4>
            <img class="chart-img" src="data:image/png;base64,{{ resultado.heatmap }}" alt="Heatmap">
        </div>
    </div>
    {% endif %}

    {% else %}
    <!-- No file yet -->
    <div class="content-card" style="text-align:center; padding: 3rem 1rem; color: var(--gris-s);">
        <div style="font-size:3.5rem; margin-bottom:1rem;">📂</div>
        <p style="font-size:1rem; font-weight:600;">Sube un archivo CSV para comenzar el análisis</p>
        <p style="font-size:.85rem; margin-top:.3rem;">Se generarán estadísticas, gráficas y mapas de calor automáticamente</p>
    </div>
    {% endif %}

</div><!-- /container-main -->

<script>
function showTab(name, btn) {
    // hide all panels
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    // deactivate all buttons
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    // show target panel
    var panel = document.getElementById('panel-' + name);
    if (panel) panel.classList.add('active');
    btn.classList.add('active');
}

function selectCol(btn, colName) {
    // deactivate buttons
    document.querySelectorAll('.col-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    // hide all stat blocks
    document.querySelectorAll('.stat-col-block').forEach(b => b.style.display = 'none');
    // show matching block
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


@app.route("/", methods=["GET", "POST"])
def inicio():
    resultado = None

    if request.method == "POST":
        archivo = request.files.get("archivo")

        if not archivo or not archivo.filename.endswith(".csv"):
            return "<h2>Solo se permiten archivos CSV</h2>"

        try:
            df = pd.read_csv(archivo)
        except Exception:
            return "<h2>Error al leer el archivo CSV</h2>"

        resultado = {}
        resultado["filas"] = df.shape[0]
        resultado["columnas"] = df.shape[1]

        # ── Tipos de datos ──────────────────────────────────────────────
        tipos_df = pd.DataFrame(df.dtypes, columns=["Tipo de Dato"])
        tipos_df["Tipo de Dato"] = tipos_df["Tipo de Dato"].astype(str)
        resultado["tipos"] = tipos_df.to_html(
            classes="table table-striped table-hover",
            border=0
        )

        # Gráfico de distribución de tipos
        tipo_counts = tipos_df["Tipo de Dato"].value_counts()
        colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        fig, ax = plt.subplots(figsize=(6, 3.5))
        bars = ax.barh(
            tipo_counts.index.tolist(),
            tipo_counts.values,
            color=colors[:len(tipo_counts)],
            edgecolor='white',
            height=0.5
        )
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

        # ── Nulos ────────────────────────────────────────────────────────
        nulos_serie = df.isnull().sum()
        nulos_pct = (nulos_serie / len(df) * 100).round(1)
        nulos_df = pd.DataFrame({
            "Valores Nulos": nulos_serie,
            "% Nulos": nulos_pct
        })

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

        # ── Valores únicos ───────────────────────────────────────────────
        resultado["unicos"] = pd.DataFrame(
            df.nunique(), columns=["Valores Únicos"]
        ).to_html(classes="table table-striped table-hover", border=0)

        # ── Columnas numéricas ───────────────────────────────────────────
        numericas = df.select_dtypes(include=np.number)
        resultado["num_numericas"] = len(numericas.columns)
        resultado["num_texto"] = len(df.select_dtypes(exclude=np.number).columns)
        resultado["columnas_num"] = list(numericas.columns)

        resultado["stats_por_col"] = {}
        resultado["histograma"] = ""
        resultado["heatmap"] = ""

        if len(numericas.columns) > 0:

            # Per-column stats + individual histograms
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
                sns.histplot(serie, kde=True, ax=ax, color='#2563eb',
                             edgecolor='white', alpha=0.8)
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

            # Global histogram (first column, for the Distribución tab)
            first_col = numericas.columns[0]
            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor('#f8fafc')
            ax.set_facecolor('#f8fafc')
            sns.histplot(numericas[first_col], kde=True, ax=ax,
                         color='#2563eb', edgecolor='white', alpha=0.8)
            ax.set_title(f"Distribución de {first_col}", fontsize=12, fontweight='bold')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            resultado["histograma"] = fig_to_b64(fig)

            # Heatmap (only if more than 1 numeric column)
            if len(numericas.columns) > 1:
                fig, ax = plt.subplots(figsize=(8, 6))
                fig.patch.set_facecolor('#f8fafc')
                ax.set_facecolor('#f8fafc')
                sns.heatmap(
                    numericas.corr(),
                    annot=True,
                    fmt=".2f",
                    cmap="Blues",
                    ax=ax,
                    linewidths=.5,
                    annot_kws={"size": 9}
                )
                ax.set_title("Mapa de Calor — Correlaciones", fontsize=12, fontweight='bold', pad=12)
                resultado["heatmap"] = fig_to_b64(fig)

    return render_template_string(HTML, resultado=resultado)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
