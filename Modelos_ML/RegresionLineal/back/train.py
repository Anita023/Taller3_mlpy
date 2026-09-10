import joblib
import numpy as np
#import matplotlib.pyplot as plt
from pathlib import Path 
from sklearn.linear_model import LinearRegression

#Predecir precios de viviendas segun la superficie en 

# # Datos de entrenamiento (x) y etiquetas (y)
x = np.array([[40], [50], [60], [85], [100], [120]])
y = np.array([210000000, 300000000, 350000000, 500000000, 600000000, 700000000])

# #Entrenar el modelo de regresión lineal
model = LinearRegression()
model.fit(x, y)

# #prediciones de prueba
# y_pred = model.predict(x)

# #Imprimir la informacion del modelo entrenado
# print("Coeficiente de Regresión:", model.coef_[0])
# print("Término independiente:", model.intercept_)

# #Graficar datos reales
# plt.scatter(x, y, color='red', label='Datos de Entrenamiento')

# #Graficar los datos de entrenamiento y la linea de regresion
# plt.plot(x, y_pred, color='blue', linewidth=2, label='Línea de Regresión')
# plt.xlabel('Superficie (m²)')
# plt.ylabel('Precio (COP)')
# plt.title('Regresión Lineal: Precio de viviendas segun la Superficie (m2)')
# plt.grid(True)
# plt.legend()
# plt.show()

#Guardar el artefacto del modelo entrenado en un archivo

BASE_DIR = Path (__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models/linear_model.joblib"
joblib.dump(model, MODEL_PATH)