from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np
import base64
import os

app = Flask(__name__, static_folder="../public")

# ==============================
# CARGAR CLASIFICADOR DE ROSTROS
# ==============================

CASCADE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "haarcascade_frontalface_default.xml"
)

# Comprobar que existe el archivo XML
if not os.path.exists(CASCADE_PATH):
    raise FileNotFoundError(
        f"No se encontró el archivo XML: {CASCADE_PATH}"
    )

# Cargar clasificador
face_classifier = cv2.CascadeClassifier(CASCADE_PATH)

# Comprobar que se cargó correctamente
if face_classifier.empty():
    raise RuntimeError(
        "No se pudo cargar el clasificador Haar Cascade."
    )


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/detect", methods=["POST"])
def detect_faces():

    if "image" not in request.files:
        return jsonify({
            "error": "No se proporcionó ninguna imagen"
        }), 400

    file = request.files["image"]

    try:

        # Leer imagen
        filestr = file.read()

        # Convertir a array
        npimg = np.frombuffer(filestr, np.uint8)

        # Decodificar imagen
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({
                "error": "Formato de imagen inválido"
            }), 400

        # Crear copia para dibujar
        output_img = img.copy()

        # Convertir a escala de grises
        gray_image = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )

        # Detectar rostros
        faces = face_classifier.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40)
        )

        # Dibujar rectángulos
        for x, y, w, h in faces:

            cv2.rectangle(
                output_img,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                3
            )

        # Convertir imagen a JPG
        _, buffer = cv2.imencode(
            ".jpg",
            output_img
        )

        # Codificar en Base64
        encoded_image = base64.b64encode(
            buffer
        ).decode("utf-8")

        return jsonify({
            "success": True,
            "faces_detected": len(faces),
            "image": f"data:image/jpeg;base64,{encoded_image}"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


app.debug = False


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )