import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# 1. Cargar el Dataset
df = pd.read_csv("rendimiento_estudiantes.csv")
print(df.describe())
print(df.head())

# 2. Graficar los datos para ver la distribución
plt.figure(figsize=(8, 8))

sns.scatterplot(
    data=df,
    x="horas_estudio",
    y="calif_practicas",
    hue="aprobado",
    palette={0: "red", 1: "green"},
    alpha=0.7,
    style="aprobado",
    s=80
)

plt.title("Distribución de resultados de estudiantes")
plt.xlabel("Horas de estudio semanales")
plt.ylabel("Calificación de prácticas")
plt.grid(True)
plt.show()

#3.Seleccionar las caracteristicas

X = df[["horas_estudio", "calif_practicas"]]
y = df["aprobado"]
#4. Dividir los datos de entrenamiento y datos de p
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=123,
    stratify=y
)

print(f"Datos totales{len(X)}")
print(f"Datos entrenamiento{len(X_train)}")
print(f"Datos prueba{len(X_test)}")

#5. Seleccionar modelo
modelo = LogisticRegression()

#6. Entrenar modelo
modelo.fit(X_train, y_train)
#7.Parametros calculados ppor la funcionn sigmodfe
print(f"Coeficient para horas_estudio:{modelo.coef_[0][0]:6f}")
print(f"Coeficient para calif_practicas:{modelo.coef_[0][1]:6f}")
print(f"Interseccion(sesgo):{modelo.intercept_[0]:6f}")

#8. Realizar predicciones
y_pred =modelo.predict(X_test)
comparar = pd.DataFrame({
    "Real": y_test,
    "Predicho": y_pred
})
print(comparar.head())
#9. Evaluar modelo
exactitud = accuracy_score(y_test,y_pred)
matrix = confusion_matrix(y_test,y_pred)
print(f"Exactitud del modelo (accurary) : {exactitud}")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Reprobado","Aprobado"]
    )
)
#10. Visualizar los datos 
sns.heatmap(
    matrix,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Predicho Reprobado", "Predicho Aprobado"],
    yticklabels=["Real Reprobado", "Real Aprobado"]
)

plt.title("Matriz de confusión")
plt.xlabel("Predicción")
plt.ylabel("Valor real")
plt.show()