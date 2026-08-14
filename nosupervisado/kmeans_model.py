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
plt.figure(figsize=(8,8))

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

##3. Seleccionar las caracteristicas 
## Nota: en aprendizaje no supervisado solo tenemos la 
## matriz de X y no exite una variable independiente (y)

X = df[["ingresos_mensuales", "gastos_mensuales"]]

## 4. Dividir lo datos (Entrenamiento/prueba)
X_train, X_test = train_test_split(X, test_size=0.2, random_state=123)
print(f"Datos totales: {len(X)}")
print(f"Datos de entrenamiento:{len(X_train)}")
print(f"Datos de prueba:{len(X_test)}")

##5. 
num_clusters = 4
modelo = KMeans(
    n_clusters = num_clusters,
    init="k-means++",
    random_state=42,
    n_init=10
)
modelo.fit(X_train)
print(f"Numero de clusters: {modelo.n_clusters}")
print(f"coordenadas de os centroides:{modelo.cluster_centers_}")

##6. Prediccion (asignacion de cluster)

cluster_predichos = modelo.predict(X_test)
comparar = X_test.copy().head()
comparar ["Cluster asignado"] = cluster_predichos[:5]
print(comparar)


##7. Evaluar el modelo
inercia = modelo.inertia_ #Suma de las distancias al cuadrado
coef_silueta = silhouette_score(X_train, modelo.labels_)
print(f"Inercia del modelo {inercia:2f} menor es mejor")
print(f"Coeficiente de silueta {coef_silueta:2f} rango -1 a 1.") ## mas pegado al uno mas cercano al 1 se pueden ver mas las agrupaciones estan muy separados pero si esta mas cerca al 1 estan mas cerca los clousters

##8. Visualizar los resultados 

plt.figure(figsize=(8,8))

sns.scatterplot(
    x=X_test["ingresos_mensuales"],
    y=X_test["gastos_mensuales"],
    hue=cluster_predichos,
    palette="Set1",
    s=100,
    alpha=0.6
)

centroides = modelo.cluster_centers_

plt.scatter(
    centroides[:,0],
    centroides[:,1],
    s=250,
    c="red",
    marker="X",
    label="Centroides"
)

plt.title("Segmentación con K-Means")
plt.xlabel("Ingresos mensuales (miles de $)")
plt.ylabel("Gastos mensuales (miles de $)")
plt.legend()
plt.grid(True)

plt.savefig("distribucion_clientes.png")
plt.show()

##9. Exportar el modelo a un archivo 
joblib.dump(modelo, "clusters_kmeans.plk")


## 10. Cargar el modelo
modelo_cargando = joblib.load("clusters_kmeans.plk")

## 11. Pruebas
nuevos_clientes = pd.DataFrame({
    "ingresos_mensuales": [35, 65, 80, 85, 50, 5],
    "gastos_mensuales": [70, 200, 100, 21, 45, 24]
})

# Predecir el segmento de los nuevos clientes
segmentos_nuevos_clientes = modelo_cargando.predict(nuevos_clientes)

# Etiquetas de los segmentos
etiquetas_segmentos = {
    0: "Ganan mucho / gastan poco",
    1: "Ganan poco / gastan mucho",
    2: "Ganan mucho / gastan mucho",
    3: "Equilibrados"
}

# Mostrar resultados
for i in range(len(nuevos_clientes)):
    ingresos = nuevos_clientes.loc[i, "ingresos_mensuales"]
    gastos = nuevos_clientes.loc[i, "gastos_mensuales"]
    cluster_id = segmentos_nuevos_clientes[i]
    nombre_segmento = etiquetas_segmentos.get(cluster_id, "Desconocido")

    print(
        f"Cliente {i + 1}: "
        f"Ingreso: ${ingresos}k, "
        f"Gastos: ${gastos}k, "
        f"Cluster: {cluster_id}, "
        f"Segmento: {nombre_segmento}"
    )