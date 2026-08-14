import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# 1. Cargar el dataset
df = pd.read_csv("clientes_ecommerce.csv")
print(df.describe())

# 2. Graficar la distribución
plt.figure(figsize=(8, 8))

sns.scatterplot(
    data=df,
    x="ingresos_mensuales",
    y="gastos_mensuales",
    color="orange",
    alpha=0.6,
    s=70
)

plt.title("Distribución de clientes potenciales")
plt.xlabel("Ingresos mensuales (miles de $)")
plt.ylabel("Gastos mensuales (miles de $)")
plt.grid(True)

plt.savefig("distribucion_clientes.png")
plt.show()

# 3. Seleccionar características
X = df[["ingresos_mensuales", "gastos_mensuales"]]

# 4. Dividir datos
X_train, X_test = train_test_split(
    X,
    test_size=0.2,
    random_state=123
)

print(f"Datos totales: {len(X)}")
print(f"Datos de entrenamiento: {len(X_train)}")
print(f"Datos de prueba: {len(X_test)}")

# 5. Entrenar K-Means con 3 clusters
num_clusters = 3

modelo = KMeans(
    n_clusters=num_clusters,
    init="k-means++",
    random_state=42,
    n_init=10
)

modelo.fit(X_train)

print(f"Número de clusters: {modelo.n_clusters}")
print("Centroides:")
print(modelo.cluster_centers_)

# 6. Predicción
cluster_predichos = modelo.predict(X_test)

comparar = X_test.copy().head()
comparar["Cluster asignado"] = cluster_predichos[:5]
print(comparar)

# 7. Evaluación
inercia = modelo.inertia_
coef_silueta = silhouette_score(X_train, modelo.labels_)

print(f"Inercia: {inercia:.2f}")
print(f"Coeficiente de silueta: {coef_silueta:.2f}")

# 8. Visualización
plt.figure(figsize=(8, 8))

sns.scatterplot(
    x=X_test["ingresos_mensuales"],
    y=X_test["gastos_mensuales"],
    hue=cluster_predichos,
    palette="Set1",
    s=100,
    alpha=0.7
)

centroides = modelo.cluster_centers_

plt.scatter(
    centroides[:, 0],
    centroides[:, 1],
    c="red",
    s=250,
    marker="X",
    label="Centroides"
)

plt.title("Segmentación con K-Means (3 Clusters)")
plt.xlabel("Ingresos mensuales (miles de $)")
plt.ylabel("Gastos mensuales (miles de $)")
plt.legend()
plt.grid(True)

plt.savefig("segmentacion_kmeans_3clusters.png")
plt.show()

# 9. Guardar modelo
joblib.dump(modelo, "clusters_kmeans.pkl")

# 10. Cargar modelo
modelo_cargando = joblib.load("clusters_kmeans.pkl")

# 11. Probar con nuevos clientes
nuevos_clientes = pd.DataFrame({
    "ingresos_mensuales": [35, 65, 80, 85, 50, 5],
    "gastos_mensuales": [70, 200, 100, 21, 45, 24]
})

segmentos_nuevos_clientes = modelo_cargando.predict(nuevos_clientes)

# Etiquetas para 3 clusters
etiquetas_segmentos = {
    0: "Ingresos y gastos bajos",
    1: "Ingresos y gastos altos",
    2: "Ingresos altos / gastos moderados"
}

print("\nResultados de nuevos clientes:\n")

for i in range(len(nuevos_clientes)):
    ingresos = nuevos_clientes.loc[i, "ingresos_mensuales"]
    gastos = nuevos_clientes.loc[i, "gastos_mensuales"]
    cluster = segmentos_nuevos_clientes[i]

    print(
        f"Cliente {i+1}: "
        f"Ingresos = ${ingresos}k, "
        f"Gastos = ${gastos}k, "
        f"Cluster = {cluster}, "
        f"Segmento = {etiquetas_segmentos.get(cluster, 'Sin etiqueta')}"
    )