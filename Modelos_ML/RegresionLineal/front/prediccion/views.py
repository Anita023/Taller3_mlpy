import requests
from django.conf import settings
from django.shortcuts import render


def predecir_precio(request):
    resultado = None
    error = None
    area_ingresada = None

    if request.method == "POST":
        area_str = request.POST.get("area_m2", "").strip()
        area_ingresada = area_str

        try:
            area_m2 = float(area_str)
            if area_m2 <= 0:
                raise ValueError("El área debe ser mayor a 0.")
        except ValueError:
            error = "Ingresa un número válido de metros cuadrados (mayor a 0)."
        else:
            try:
                response = requests.post(
                    f"{settings.FASTAPI_URL}/predict",
                    json={"area_m2": area_m2},
                    timeout=5,
                )
                if response.status_code == 200:
                    resultado = response.json()
                elif response.status_code == 503:
                    error = "El modelo de predicción no está disponible en este momento."
                else:
                    error = f"La API respondió con un error (código {response.status_code})."
            except requests.exceptions.ConnectionError:
                error = "No se pudo conectar con la API de predicción. ¿Está corriendo en " \
                        f"{settings.FASTAPI_URL}?"
            except requests.exceptions.Timeout:
                error = "La API tardó demasiado en responder. Intenta de nuevo."
            except requests.exceptions.RequestException:
                error = "Ocurrió un error inesperado al consultar la API."

    return render(
        request,
        "prediccion/index.html",
        {
            "resultado": resultado,
            "error": error,
            "area_ingresada": area_ingresada,
        },
    )
