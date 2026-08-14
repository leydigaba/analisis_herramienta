# =====================================================
# APLICACIÓN - PREDICCIÓN DEL PRECIO DE CASAS
# Interfaz gráfica en Tkinter
# =====================================================
#
# Requisitos (instalar si hace falta):
#   pip install pandas numpy scikit-learn joblib matplotlib
#
# Cómo usarla:
#   1. Coloca este archivo en la MISMA carpeta que "casas.csv"
#      (el mismo archivo que usaste para entrenar el modelo:
#      debe tener las columnas "metros_cuadrados" y "precio").
#   2. Si ya tienes "modelo_prediccion_casas.pkl" generado con tu
#      script original, la app lo cargará directamente (más rápido).
#      Si no existe, la app entrena el modelo automáticamente con
#      "casas.csv" y lo guarda para la próxima vez.
#   3. Ejecuta:  python app_prediccion_casas.py
#   4. Mueve el control deslizante para elegir los metros cuadrados
#      y presiona "Predecir Precio".
#
# =====================================================

import os
import sys
import joblib
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =====================================================
# Paleta de colores de la aplicación
# =====================================================
COLOR_PRINCIPAL = "#B78FB1"   # Botones, bordes, títulos, elementos destacados
COLOR_PRINCIPAL_HOVER = "#A67AA0"
COLOR_FONDO = "#FFFFFF"       # Blanco
COLOR_TEXTO = "#333333"
COLOR_TEXTO_SUAVE = "#666666"

RUTA_CSV = "casas.csv"
RUTA_MODELO = "modelo_prediccion_casas.pkl"


# =====================================================
# Lógica del modelo
# =====================================================
class GestorModelo:
    """Carga el modelo si existe, o lo entrena desde casas.csv."""

    def __init__(self):
        self.modelo = None
        self.metricas = {"rmse": None, "r2": None}
        self.datos = None
        self.min_m2 = 30
        self.max_m2 = 400

        self._preparar_modelo()

    def _preparar_modelo(self):
        # Intentar cargar datos para conocer rangos y graficar
        if os.path.exists(RUTA_CSV):
            df = pd.read_csv(RUTA_CSV)
            df.columns = df.columns.str.strip()
            self.datos = df
            if "metros_cuadrados" in df.columns:
                self.min_m2 = int(max(10, df["metros_cuadrados"].min()))
                self.max_m2 = int(df["metros_cuadrados"].max() + 20)

        # Si ya existe un modelo entrenado, cargarlo
        if os.path.exists(RUTA_MODELO):
            self.modelo = joblib.load(RUTA_MODELO)
            return

        # Si no existe modelo pero sí datos, entrenar uno nuevo
        if self.datos is not None and {"metros_cuadrados", "precio"}.issubset(self.datos.columns):
            X = self.datos[["metros_cuadrados"]]
            y = self.datos["precio"]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.30, random_state=123
            )

            modelo = LinearRegression()
            modelo.fit(X_train, y_train)

            y_pred = modelo.predict(X_test)
            self.metricas["rmse"] = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            self.metricas["r2"] = float(r2_score(y_test, y_pred))

            joblib.dump(modelo, RUTA_MODELO)
            self.modelo = modelo
        else:
            self.modelo = None

    def predecir(self, metros_cuadrados: float) -> float:
        if self.modelo is None:
            raise RuntimeError(
                "No hay un modelo disponible. Coloca 'casas.csv' junto a esta "
                "aplicación (o el archivo 'modelo_prediccion_casas.pkl') y vuelve a abrirla."
            )
        entrada = pd.DataFrame({"metros_cuadrados": [metros_cuadrados]})
        return float(self.modelo.predict(entrada)[0])


# =====================================================
# Interfaz gráfica
# =====================================================
class AplicacionPrediccion(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Predicción del Precio de Casas")
        self.configure(bg=COLOR_FONDO)
        self.geometry("620x680")
        self.minsize(560, 640)

        self.gestor = GestorModelo()

        self._configurar_estilos()
        self._crear_widgets()

    # -------------------------------------------------
    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Principal.TButton",
            background=COLOR_PRINCIPAL,
            foreground="white",
            font=("Segoe UI", 12, "bold"),
            padding=10,
            borderwidth=0,
            focuscolor=COLOR_FONDO,
        )
        estilo.map(
            "Principal.TButton",
            background=[("active", COLOR_PRINCIPAL_HOVER), ("pressed", COLOR_PRINCIPAL_HOVER)],
        )

        estilo.configure(
            "Horizontal.TScale",
            background=COLOR_FONDO,
            troughcolor="#F1E6EF",
        )

    # -------------------------------------------------
    def _crear_widgets(self):
        # ---------- Encabezado ----------
        marco_titulo = tk.Frame(self, bg=COLOR_FONDO, highlightbackground=COLOR_PRINCIPAL,
                                 highlightthickness=0)
        marco_titulo.pack(fill="x", pady=(25, 5), padx=25)

        titulo = tk.Label(
            marco_titulo,
            text="Predicción del Precio de Casas",
            font=("Segoe UI", 20, "bold"),
            fg=COLOR_PRINCIPAL,
            bg=COLOR_FONDO,
        )
        titulo.pack()

        subtitulo = tk.Label(
            marco_titulo,
            text="Selecciona los metros cuadrados y obtén el precio estimado",
            font=("Segoe UI", 10),
            fg=COLOR_TEXTO_SUAVE,
            bg=COLOR_FONDO,
        )
        subtitulo.pack(pady=(4, 0))

        # Línea divisoria destacada
        linea = tk.Frame(self, bg=COLOR_PRINCIPAL, height=3)
        linea.pack(fill="x", padx=25, pady=(15, 15))

        # ---------- Panel de selección (con borde destacado) ----------
        panel = tk.Frame(
            self, bg=COLOR_FONDO,
            highlightbackground=COLOR_PRINCIPAL,
            highlightcolor=COLOR_PRINCIPAL,
            highlightthickness=2,
            bd=0,
        )
        panel.pack(fill="x", padx=25, pady=(0, 15))

        etiqueta_m2 = tk.Label(
            panel, text="Metros cuadrados:",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_TEXTO, bg=COLOR_FONDO,
        )
        etiqueta_m2.pack(anchor="w", padx=15, pady=(15, 0))

        self.valor_m2 = tk.IntVar(value=int((self.gestor.min_m2 + self.gestor.max_m2) / 2))

        marco_valor = tk.Frame(panel, bg=COLOR_FONDO)
        marco_valor.pack(fill="x", padx=15, pady=(2, 5))

        self.etiqueta_valor = tk.Label(
            marco_valor,
            textvariable=self.valor_m2,
            font=("Segoe UI", 26, "bold"),
            fg=COLOR_PRINCIPAL, bg=COLOR_FONDO,
        )
        self.etiqueta_valor.pack(side="left")

        tk.Label(
            marco_valor, text=" m²",
            font=("Segoe UI", 16),
            fg=COLOR_TEXTO_SUAVE, bg=COLOR_FONDO,
        ).pack(side="left", anchor="s", pady=(0, 4))

        self.control_deslizante = ttk.Scale(
            panel,
            from_=self.gestor.min_m2,
            to=self.gestor.max_m2,
            orient="horizontal",
            style="Horizontal.TScale",
            variable=self.valor_m2,
            command=self._al_mover_control,
        )
        self.control_deslizante.pack(fill="x", padx=15, pady=(0, 8))

        # Entrada manual alternativa
        marco_entrada = tk.Frame(panel, bg=COLOR_FONDO)
        marco_entrada.pack(fill="x", padx=15, pady=(0, 15))

        tk.Label(
            marco_entrada, text="O escribe un valor exacto:",
            font=("Segoe UI", 9), fg=COLOR_TEXTO_SUAVE, bg=COLOR_FONDO,
        ).pack(side="left")

        self.entrada_m2 = tk.Entry(
            marco_entrada, width=8, font=("Segoe UI", 10),
            highlightbackground=COLOR_PRINCIPAL, highlightcolor=COLOR_PRINCIPAL,
            highlightthickness=1, relief="flat",
        )
        self.entrada_m2.pack(side="left", padx=(8, 0))
        self.entrada_m2.bind("<Return>", self._al_escribir_valor)

        boton_ir = tk.Button(
            marco_entrada, text="Ir", command=self._al_escribir_valor,
            bg=COLOR_PRINCIPAL, fg="white", relief="flat",
            font=("Segoe UI", 9, "bold"), padx=10, activebackground=COLOR_PRINCIPAL_HOVER,
        )
        boton_ir.pack(side="left", padx=6)

        # ---------- Botón de predicción ----------
        self.boton_predecir = ttk.Button(
            self, text="Predecir Precio",
            style="Principal.TButton",
            command=self._al_predecir,
        )
        self.boton_predecir.pack(pady=(5, 15), ipadx=10)

        # ---------- Resultado ----------
        marco_resultado = tk.Frame(
            self, bg="#FBF5FA",
            highlightbackground=COLOR_PRINCIPAL,
            highlightthickness=2,
        )
        marco_resultado.pack(fill="x", padx=25, pady=(0, 15))

        tk.Label(
            marco_resultado, text="PRECIO ESTIMADO",
            font=("Segoe UI", 9, "bold"), fg=COLOR_TEXTO_SUAVE, bg="#FBF5FA",
        ).pack(pady=(12, 0))

        self.etiqueta_resultado = tk.Label(
            marco_resultado, text="—",
            font=("Segoe UI", 26, "bold"), fg=COLOR_PRINCIPAL, bg="#FBF5FA",
        )
        self.etiqueta_resultado.pack(pady=(0, 12))

        # ---------- Gráfica ----------
        self.figura, self.eje = plt.subplots(figsize=(5.2, 3.2), dpi=100)
        self.canvas_grafica = FigureCanvasTkAgg(self.figura, master=self)
        self.canvas_grafica.get_tk_widget().pack(fill="both", expand=True, padx=25, pady=(0, 15))
        self._dibujar_grafica()

        # ---------- Pie con métricas del modelo ----------
        texto_metricas = self._texto_metricas()
        tk.Label(
            self, text=texto_metricas,
            font=("Segoe UI", 9), fg=COLOR_TEXTO_SUAVE, bg=COLOR_FONDO,
        ).pack(pady=(0, 10))

    # -------------------------------------------------
    def _texto_metricas(self):
        rmse = self.gestor.metricas.get("rmse")
        r2 = self.gestor.metricas.get("r2")
        if rmse is not None and r2 is not None:
            return f"Modelo entrenado  ·  RMSE: {rmse:,.2f}   R²: {r2:.2f}"
        elif os.path.exists(RUTA_MODELO):
            return "Modelo cargado desde modelo_prediccion_casas.pkl"
        else:
            return "⚠ No se encontró casas.csv ni el modelo entrenado."

    # -------------------------------------------------
    def _al_mover_control(self, _evento=None):
        self._dibujar_grafica()

    def _al_escribir_valor(self, _evento=None):
        texto = self.entrada_m2.get().strip()
        if not texto:
            return
        try:
            valor = float(texto)
            minimo, maximo = self.control_deslizante.cget("from"), self.control_deslizante.cget("to")
            valor = max(float(minimo), min(float(maximo), valor))
            self.valor_m2.set(int(valor))
            self._dibujar_grafica()
        except ValueError:
            messagebox.showwarning("Valor inválido", "Escribe un número válido de metros cuadrados.")

    def _al_predecir(self):
        try:
            metros = self.valor_m2.get()
            precio = self.gestor.predecir(metros)
            self.etiqueta_resultado.config(text=f"${precio:,.2f}")
            self._dibujar_grafica(precio_predicho=precio)
        except RuntimeError as error:
            messagebox.showerror("Modelo no disponible", str(error))
        except Exception as error:
            messagebox.showerror("Error", f"Ocurrió un problema al predecir:\n{error}")

    # -------------------------------------------------
    def _dibujar_grafica(self, precio_predicho=None):
        self.eje.clear()

        if self.gestor.datos is not None and {"metros_cuadrados", "precio"}.issubset(self.gestor.datos.columns):
            self.eje.scatter(
                self.gestor.datos["metros_cuadrados"],
                self.gestor.datos["precio"],
                color=COLOR_PRINCIPAL, alpha=0.5, s=25, label="Datos históricos",
            )

            if self.gestor.modelo is not None:
                rango_x = np.linspace(self.gestor.min_m2, self.gestor.max_m2, 100).reshape(-1, 1)
                rango_df = pd.DataFrame(rango_x, columns=["metros_cuadrados"])
                rango_y = self.gestor.modelo.predict(rango_df)
                self.eje.plot(rango_x, rango_y, color="#7A5A76", linewidth=2, label="Línea de regresión")

        metros_actuales = self.valor_m2.get()
        if precio_predicho is not None:
            self.eje.scatter(
                [metros_actuales], [precio_predicho],
                color="#333333", s=90, zorder=5, marker="D", label="Predicción actual",
            )
        else:
            self.eje.axvline(metros_actuales, color="#B78FB1", linestyle="--", linewidth=1, alpha=0.6)

        self.eje.set_xlabel("Metros cuadrados", fontsize=9)
        self.eje.set_ylabel("Precio", fontsize=9)
        self.eje.tick_params(labelsize=8)
        self.eje.legend(fontsize=7, loc="upper left")
        self.eje.grid(alpha=0.3)
        self.figura.tight_layout()
        self.canvas_grafica.draw()


# =====================================================
# Punto de entrada
# =====================================================
if __name__ == "__main__":
    app = AplicacionPrediccion()
    app.mainloop()