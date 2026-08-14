# =====================================================
# REGRESIÓN LINEAL - PREDICCIÓN DEL PRECIO DE CASAS
# =====================================================

# 1. Importar librerías
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


# =====================================================
# 2. Cargar el conjunto de datos
# =====================================================
df = pd.read_csv("casas.csv")

# Eliminar espacios en blanco de los nombres de las columnas
df.columns = df.columns.str.strip()

# Mostrar las columnas disponibles
print("Columnas del archivo:")
print(df.columns)

# Mostrar estadísticas descriptivas
print("\nEstadísticas del conjunto de datos:")
print(df.describe())


# =====================================================
# 3. Visualizar los datos
# =====================================================
plt.figure(figsize=(8, 6))

sns.scatterplot(
    data=df,
    x="metros_cuadrados",
    y="precio",
    color="blue",
    alpha=0.7
)

plt.title("Relación entre metros cuadrados y precio")
plt.xlabel("Metros cuadrados")
plt.ylabel("Precio")
plt.grid(True)

plt.show()


# =====================================================
# 4. Seleccionar variables
# =====================================================

# Variable independiente (X)
X = df[["metros_cuadrados"]]

# Variable dependiente (y)
y = df["precio"]


# =====================================================
# 5. Dividir los datos
# 70% entrenamiento - 30% prueba
# =====================================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=123
)

print("\nCantidad de registros")
print(f"Total de datos: {len(X)}")
print(f"Datos de entrenamiento: {len(X_train)}")
print(f"Datos de prueba: {len(X_test)}")

print("\nPrimeros datos de entrenamiento:")
print(X_train.head())


# =====================================================
# 6. Crear el modelo
# =====================================================
modelo = LinearRegression()


# =====================================================
# 7. Entrenar el modelo
# =====================================================
modelo.fit(X_train, y_train)

# Ecuación:
# Precio = (coeficiente × metros cuadrados) + intercepto

print("\nModelo entrenado")
print(f"Coeficiente: {modelo.coef_[0]:.4f}")
print(f"Intercepto: {modelo.intercept_:.4f}")


# =====================================================
# 8. Realizar predicciones
# =====================================================
y_pred = modelo.predict(X_test)


# =====================================================
# 9. Comparar valores reales vs predicciones
# =====================================================
comparativa = pd.DataFrame({
    "Precio real": y_test,
    "Precio predicho": y_pred
})

print("\nComparación de resultados:")
print(comparativa.head())


# =====================================================
# 10. Evaluar el modelo
# =====================================================

# Error cuadrático medio (RMSE)
rmse = math.sqrt(mean_squared_error(y_test, y_pred))

# Coeficiente de determinación
r2 = r2_score(y_test, y_pred)

print("\nEvaluación del modelo")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.2f}")

plt.figure(figsize=(8,8))
plt.scatter(X_test,y_test,color='blue', label='Datos reales test', alpha=0.7)
plt.plot(X_test,y_pred, color='red',linewidth=2, label='Linea de regresion')
plt.title("Regresion lineal")
plt.xlabel('Metros cuadrados')
plt.ylabel('precio en millones')
plt.legend()
plt.grid(True)
plt.show()

# =====================================================
# 9. Exportar el modelo
# =====================================================
joblib.dump(modelo,"modelo_prediccion_casas.pkl")

# =====================================================
# 10. cargar el modelo
# =====================================================
modelo_cargado = joblib.load(modelo,"modelo_prediccion_casas.pkl")
# =====================================================
# 11. Realizar predicciones cpon el modelo cargado
# =====================================================
datos_prueba =pd.DataFrame({
    "metros_cuadrados":[100,150,320]
})
precios_predichos = modelo_cargado.predict(datos_prueba)

# =====================================================
# REGRESIÓN LINEAL - PREDICCIÓN DEL PRECIO DE CASAS
# =====================================================

# 1. Importar librerías
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


# =====================================================
# 2. Cargar el conjunto de datos
# =====================================================
df = pd.read_csv("casas.csv")

# Eliminar espacios en blanco de los nombres de las columnas
df.columns = df.columns.str.strip()

# Mostrar las columnas disponibles
print("Columnas del archivo:")
print(df.columns)

# Mostrar estadísticas descriptivas
print("\nEstadísticas del conjunto de datos:")
print(df.describe())


# =====================================================
# 3. Visualizar los datos
# =====================================================
plt.figure(figsize=(8, 6))

sns.scatterplot(
    data=df,
    x="metros_cuadrados",
    y="precio",
    color="blue",
    alpha=0.7
)

plt.title("Relación entre metros cuadrados y precio")
plt.xlabel("Metros cuadrados")
plt.ylabel("Precio")
plt.grid(True)

plt.show()


# =====================================================
# 4. Seleccionar variables
# =====================================================

# Variable independiente (X)
X = df[["metros_cuadrados"]]

# Variable dependiente (y)
y = df["precio"]


# =====================================================
# 5. Dividir los datos
# 70% entrenamiento - 30% prueba
# =====================================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=123
)

print("\nCantidad de registros")
print(f"Total de datos: {len(X)}")
print(f"Datos de entrenamiento: {len(X_train)}")
print(f"Datos de prueba: {len(X_test)}")

print("\nPrimeros datos de entrenamiento:")
print(X_train.head())


# =====================================================
# 6. Crear el modelo
# =====================================================
modelo = LinearRegression()


# =====================================================
# 7. Entrenar el modelo
# =====================================================
modelo.fit(X_train, y_train)

# Ecuación:
# Precio = (coeficiente × metros cuadrados) + intercepto

print("\nModelo entrenado")
print(f"Coeficiente: {modelo.coef_[0]:.4f}")
print(f"Intercepto: {modelo.intercept_:.4f}")


# =====================================================
# 8. Realizar predicciones
# =====================================================
y_pred = modelo.predict(X_test)


# =====================================================
# 9. Comparar valores reales vs predicciones
# =====================================================
comparativa = pd.DataFrame({
    "Precio real": y_test,
    "Precio predicho": y_pred
})

print("\nComparación de resultados:")
print(comparativa.head())


# =====================================================
# 10. Evaluar el modelo
# =====================================================

# Error cuadrático medio (RMSE)
rmse = math.sqrt(mean_squared_error(y_test, y_pred))

# Coeficiente de determinación
r2 = r2_score(y_test, y_pred)

print("\nEvaluación del modelo")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.2f}")

plt.figure(figsize=(8,8))
plt.scatter(X_test,y_test,color='blue', label='Datos reales test', alpha=0.7)
plt.plot(X_test,y_pred, color='red',linewidth=2, label='Linea de regresion')
plt.title("Regresion lineal")
plt.xlabel('Metros cuadrados')
plt.ylabel('precio en millones')
plt.legend()
plt.grid(True)
plt.show()

# =====================================================
# 9. Exportar el modelo
# =====================================================
joblib.dump(modelo, "modelo_prediccion_casas.pkl")

# =====================================================
# 10. cargar el modelo
# =====================================================
modelo_cargado = joblib.load("modelo_prediccion_casas.pkl")
# =====================================================

# 11. Realizar predicciones cpon el modelo cargado
# =====================================================
datos_prueba =pd.DataFrame({
    "metros_cuadrados":[100,150,320]
})
precios_predichos = modelo_cargado.predict(datos_prueba)

# =====================================================
# 12. Realizar predicciones cpon el modelo cargado
# =====================================================
for valores in precios_predichos:
    print (f"VALORES: {valores}")
 