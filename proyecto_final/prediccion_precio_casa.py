import os
import math
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CASAS_CSV = os.path.join(BASE_DIR, "casas.csv")


def cargar_datos_originales():
    df = pd.read_csv(CASAS_CSV)
    df.columns = df.columns.str.strip()
    return df


def entrenar_modelo(df):
    X = df[["metros_cuadrados"]]
    y = df["precio"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=123
    )

    modelo = LinearRegression()
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    rmse = math.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    return modelo, rmse, r2


def mostrar_prediccion():
    st.markdown("""
        <style>
            .stApp { background-color: #ffffff; }
            h1 { color: #9a6f94; text-align: center; }
            h3 { color: #9a6f94; }
            p.subtitle { text-align: center; color: #7a7280; margin-top: -10px; }
            div.stButton > button {
                background-color: #B78FB1;
                color: white;
                border-radius: 10px;
                border: none;
                font-weight: 700;
                font-size: 15px;
                padding: 0.6em 1.2em;
                width: 100%;
            }
            div.stButton > button:hover {
                background-color: #9a6f94;
                color: white;
            }
            .result-box {
                background-color: #f2e9f1;
                border: 2px solid #B78FB1;
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                margin-top: 10px;
            }
            .result-box .price {
                font-size: 36px;
                font-weight: 800;
                color: #9a6f94;
            }
            [data-testid="stNumberInput"] label { color: #9a6f94; font-weight: 700; }
            [data-testid="stFileUploader"] { border: 1.5px dashed #B78FB1; border-radius: 12px; padding: 6px; }
            hr { border-color: #f2e9f1; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>Predicción del Precio de tu Casa</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Ingresa los metros cuadrados y obtén una predicción al instante</p>", unsafe_allow_html=True)

    if "df_prediccion" not in st.session_state:
        st.session_state.df_prediccion = cargar_datos_originales()

    with st.expander("⚙️ Administrar los datos de entrenamiento"):
        st.markdown("**1. Subir un archivo CSV**")
        st.caption("Debe tener las columnas: metros_cuadrados, precio")
        archivo = st.file_uploader("Sube un CSV", type=["csv"], label_visibility="collapsed")

        col_up1, col_up2 = st.columns(2)
        if archivo is not None:
            if col_up1.button(" Usar este archivo y re-entrenar"):
                nuevo_df = pd.read_csv(archivo)
                nuevo_df.columns = nuevo_df.columns.str.strip()
                st.session_state.df_prediccion = nuevo_df
                st.success(f"Datos actualizados: {len(nuevo_df)} registros cargados. Modelo re-entrenado.")

        if col_up2.button("↩Volver a los datos originales"):
            st.session_state.df_prediccion = cargar_datos_originales()
            st.success("Se restauraron los datos originales (casas.csv). Modelo re-entrenado.")

        st.markdown("---")
        st.markdown("**2. Agregar un nuevo registro**")

        col_m1, col_m2, col_m3 = st.columns([1, 1, 1])
        nuevo_m2 = col_m1.number_input("Metros cuadrados", min_value=1, value=100, step=1)
        nuevo_precio = col_m2.number_input("Precio", min_value=0.0, value=1500000.0, step=1000.0, format="%.2f")

        if col_m3.button("Agregar dato"):
            fila_nueva = pd.DataFrame({"metros_cuadrados": [nuevo_m2], "precio": [nuevo_precio]})
            st.session_state.df_prediccion = pd.concat([st.session_state.df_prediccion, fila_nueva], ignore_index=True)
            st.success(f"Dato agregado: {nuevo_m2} m² → ${nuevo_precio:,.0f}. Modelo actualizado con toda la información.")

        st.caption(f"Registros usados actualmente: **{len(st.session_state.df_prediccion)}**")

    df = st.session_state.df_prediccion
    modelo, rmse, r2 = entrenar_modelo(df)

    m2 = st.number_input(
        "Metros cuadrados de la casa",
        min_value=int(df.metros_cuadrados.min()),
        max_value=int(df.metros_cuadrados.max()) * 2,
        value=150,
        step=1,
    )

    calcular = st.button("Calcular precio")

    if calcular:
        datos_prueba = pd.DataFrame({"metros_cuadrados": [m2]})
        precio_predicho = modelo.predict(datos_prueba)[0]

        st.markdown(f"""
            <div class="result-box">
                <div style="font-size:13px; color:#9a6f94; text-transform:uppercase; font-weight:700;">
                    Precio estimado para {m2} m²
                </div>
                <div class="price">${precio_predicho:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("Plano de la casa")

        lado = math.sqrt(m2)
        ancho_sala = 0.55 * lado
        ancho_der = 0.45 * lado
        alto_der = lado / 2

        fig1, ax1 = plt.subplots(figsize=(2.6, 2.6), dpi=150)
        ax1.add_patch(patches.Rectangle((0, 0), lado, lado, fill=False, edgecolor="#9a6f94", linewidth=2))
        ax1.add_patch(patches.Rectangle((0, 0), ancho_sala, lado, fill=True, facecolor="#f2e9f1", edgecolor="#B78FB1", linewidth=1))
        ax1.text(ancho_sala / 2, lado / 2, "Sala /\nComedor", ha="center", va="center", fontsize=6, color="#9a6f94")
        ax1.add_patch(patches.Rectangle((ancho_sala, alto_der), ancho_der, alto_der, fill=True, facecolor="#e9d9e6", edgecolor="#B78FB1", linewidth=1))
        ax1.text(ancho_sala + ancho_der / 2, alto_der + alto_der / 2, "Habitación", ha="center", va="center", fontsize=6, color="#9a6f94")
        ax1.add_patch(patches.Rectangle((ancho_sala, 0), ancho_der, alto_der, fill=True, facecolor="#f2e9f1", edgecolor="#B78FB1", linewidth=1))
        ax1.text(ancho_sala + ancho_der / 2, alto_der / 2, "Cocina /\nBaño", ha="center", va="center", fontsize=6, color="#9a6f94")
        ax1.set_xlim(-0.5, lado + 0.5)
        ax1.set_ylim(-0.5, lado + 0.5)
        ax1.set_aspect("equal")
        ax1.axis("off")
        ax1.set_title(f"{lado:.1f} m × {lado:.1f} m = {m2} m²", fontsize=7, color="#7a7280")
        fig1.tight_layout(pad=0.3)

        col_plano1, col_plano2, col_plano3 = st.columns([1, 1, 1])
        with col_plano2:
            st.pyplot(fig1, use_container_width=False)

        st.subheader("Gráfica de dispersión con tu predicción")
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        ax2.scatter(df["metros_cuadrados"], df["precio"], color="#B78FB1", alpha=0.5, label="Datos reales")

        x_line = np.linspace(df.metros_cuadrados.min(), max(df.metros_cuadrados.max(), m2), 100)
        y_line = modelo.predict(pd.DataFrame({"metros_cuadrados": x_line}))
        ax2.plot(x_line, y_line, color="#9a6f94", linewidth=2.5, label="Línea de regresión")

        ax2.scatter([m2], [precio_predicho], color="white", edgecolor="#9a6f94", s=160, linewidth=3, zorder=5, label="Tu predicción")
        ax2.set_xlabel("Metros cuadrados")
        ax2.set_ylabel("Precio")
        ax2.legend()
        ax2.grid(alpha=0.2)

        st.pyplot(fig2)
