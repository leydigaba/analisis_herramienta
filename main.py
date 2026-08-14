from flask import Flask, request, render_template_string
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import base64

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

        body{
            background:#f4f6f9;
        }

        .card{
            border:none;
            border-radius:15px;
            box-shadow:0 4px 15px rgba(0,0,0,0.1);
        }

        .titulo{
            color:#0d6efd;
            font-weight:bold;
        }

        img{
            width:100%;
            border-radius:10px;
        }

        table{
            width:100% !important;
        }

        .table{
            margin-top:10px;
        }

    </style>

</head>

<body>

<div class="container py-5">

    <div class="card p-4">

        <h1 class="text-center titulo">
            📊 Herramienta de Análisis CSV
        </h1>

        <p class="text-center text-muted">
            Carga un archivo CSV y obtén estadísticas automáticas
        </p>

        <form method="POST" enctype="multipart/form-data">

            <div class="mb-3">

                <input
                    type="file"
                    class="form-control"
                    name="archivo"
                    accept=".csv"
                    required>

            </div>

            <div class="d-grid">

                <button class="btn btn-primary btn-lg">
                    Analizar Archivo
                </button>

            </div>

        </form>

    </div>

    {% if resultado %}

    <div class="row mt-4">

        <div class="col-md-6">

            <div class="card p-3 h-100">

                <h4>📋 Información General</h4>

                <p><strong>Filas:</strong> {{ resultado["filas"] }}</p>

                <p><strong>Columnas:</strong> {{ resultado["columnas"] }}</p>

            </div>

        </div>

        <div class="col-md-6">

            <div class="card p-3 h-100">

                <h4>📈 Estadísticas</h4>

                {{ resultado["estadisticas"]|safe }}

            </div>

        </div>

    </div>

    <div class="card p-4 mt-4">

        <h3>🔠 Tipos de Datos</h3>

        {{ resultado["tipos"]|safe }}

    </div>

    <div class="card p-4 mt-4">

        <h3>⚠️ Valores Nulos por Columna</h3>

        {{ resultado["nulos"]|safe }}

    </div>

    <div class="card p-4 mt-4">

        <h3>🔍 Valores Únicos</h3>

        {{ resultado["unicos"]|safe }}

    </div>

    {% if resultado["histograma"] %}

    <div class="card p-4 mt-4">

        <h3>📊 Gráfica de Distribución</h3>

        <img src="data:image/png;base64,{{ resultado['histograma'] }}">

    </div>

    {% endif %}

    {% if resultado["heatmap"] %}

    <div class="card p-4 mt-4">

        <h3>🔥 Mapa de Calor</h3>

        <img src="data:image/png;base64,{{ resultado['heatmap'] }}">

    </div>

    {% endif %}

    {% endif %}

</div>

</body>

</html>
"""

@app.route("/", methods=["GET", "POST"])
def inicio():

    resultado = None

    if request.method == "POST":

        archivo = request.files["archivo"]

        if not archivo.filename.endswith(".csv"):
            return "<h2>Solo se permiten archivos CSV</h2>"

        try:
            df = pd.read_csv(archivo)
        except:
            return "<h2>Error al leer el archivo CSV</h2>"

        resultado = {}

        resultado["filas"] = df.shape[0]
        resultado["columnas"] = df.shape[1]

        resultado["tipos"] = (
            pd.DataFrame(df.dtypes, columns=["Tipo de Dato"])
            .to_html(
                classes="table table-striped table-hover",
                border=0
            )
        )

        resultado["nulos"] = (
            pd.DataFrame(
                df.isnull().sum(),
                columns=["Cantidad de Nulos"]
            )
            .to_html(
                classes="table table-striped table-hover",
                border=0
            )
        )

        resultado["unicos"] = (
            pd.DataFrame(
                df.nunique(),
                columns=["Valores Únicos"]
            )
            .to_html(
                classes="table table-striped table-hover",
                border=0
            )
        )

        numericas = df.select_dtypes(include=np.number)

        if len(numericas.columns) > 0:

            estadisticas = pd.DataFrame({
                "Mínimo": numericas.min(),
                "Máximo": numericas.max(),
                "Media": numericas.mean().round(2),
                "Mediana": numericas.median()
            })

            resultado["estadisticas"] = estadisticas.to_html(
                classes="table table-striped table-hover",
                border=0
            )

            plt.figure(figsize=(8,4))

            sns.histplot(
                numericas.iloc[:,0],
                kde=True
            )

            plt.title(
                f"Distribución de {numericas.columns[0]}"
            )

            plt.tight_layout()

            plt.savefig("histograma.png")

            plt.close()

            with open("histograma.png", "rb") as img:

                resultado["histograma"] = base64.b64encode(
                    img.read()
                ).decode()

            plt.figure(figsize=(8,6))

            sns.heatmap(
                numericas.corr(),
                annot=True,
                cmap="Blues"
            )

            plt.title("Mapa de Calor")

            plt.tight_layout()

            plt.savefig("heatmap.png")

            plt.close()

            with open("heatmap.png", "rb") as img:

                resultado["heatmap"] = base64.b64encode(
                    img.read()
                ).decode()

        else:

            resultado["estadisticas"] = """
            <div class='alert alert-warning'>
            No existen columnas numéricas.
            </div>
            """

            resultado["histograma"] = ""
            resultado["heatmap"] = ""

    return render_template_string(
        HTML,
        resultado=resultado
    )

if __name__ == "__main__":
    app.run(debug=True)