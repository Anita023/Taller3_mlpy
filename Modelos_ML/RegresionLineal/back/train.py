from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="API de Predicción de Precios de Viviendas",
    description="Esta API predice el precio de una vivienda en funcion de la superficie en metros cuadrados utilizando un modelo de regresión lineal previamente entrenado.",
    version="1.0.0",
)


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "Linear_model.joblib"

try:
    # Cargar el modelo entrenado desde el archivo
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None


class housem2(BaseModel):
    area_m2: float = Field(..., example=82.5, description="Superficie de la vivienda en metros cuadrados", gt=0)


@app.get("/")
def health_check():
    return {
        "message": "API de Predicción de Precios de Viviendas está en funcionamiento.",
        "status": "OK",
        "model_loaded": model is not None,
    }


@app.post("/predict")
def predict_price(data: housem2):
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible. Intente mas tarde")

    # Realizar la predicción utilizando el modelo cargado
    prediction = model.predict([[data.area_m2]])[0]

    return {
        "area_m2": data.area_m2,
        "predicted_price": round(float(prediction), 2),
    }