import base64
import os
from flask import Flask, jsonify, request, send_from_directory
import cv2
import numpy as np

app = Flask(__name__, static_folder="../public")

# Cargar clasificador usando las variables internas de OpenCV para Vercel
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_classifier = cv2.CascadeClassifier(CASCADE_PATH)

if face_classifier.empty():
  raise RuntimeError("No se pudo cargar el clasificador Haar Cascade.")


@app.route("/")
def serve_index():
  return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
  return send_from_directory(app.static_folder, path)


@app.route("/api/detect", methods=["POST"])
def detect_faces():
  if "image" not in request.files:
    return jsonify({"error": "No se proporcionó la clave 'image'"}), 400

  file = request.files["image"]

  try:
    filestr = file.read()
    npimg = np.frombuffer(filestr, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
      return jsonify({"error": "Formato de imagen inválido"}), 400

    output_img = img.copy()
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_classifier.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )

    for x, y, w, h in faces:
      cv2.rectangle(
          output_img, (x, y), (x + w, y + h), (0, 255, 0), 3
      )

    _, buffer = cv2.imencode(".jpg", output_img)
    encoded_image = base64.b64encode(buffer).decode("utf-8")

    return jsonify({
        "success": True,
        "faces_detected": len(faces),
        "image": f"data:image/jpeg;base64,{encoded_image}",
    })

  except Exception as e:
    return jsonify({"error": str(e)}), 500


app.debug = False

if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)