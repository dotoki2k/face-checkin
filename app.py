# app.py
import cv2
import numpy as np
from flask import Flask, request, render_template, jsonify
import base64
from handle import detect_and_identify_face
from utils import encode_known_faces

app = Flask(__name__)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# read and encode known face image.
known_encodings, known_names = encode_known_faces("known_faces/")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect_faces():
    try:
        # Validate request data
        if "image" not in request.json:
            return jsonify(error="No image data received"), 400

        image_data = request.json["image"]
        if not image_data.startswith("data:image/"):
            return jsonify(error="Invalid image format"), 400

        # Extract base64 data
        header, encoded = image_data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)

        # Validate decoded data
        if nparr.size == 0:
            return jsonify(error="Empty image data"), 400

        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify(error="Failed to decode image"), 400

        # Face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        detect_and_identify_face(img, known_encodings, known_names)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        return jsonify(
            faces=[
                {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                for (x, y, w, h) in faces
            ]
        )

    except Exception as e:
        app.logger.error(f"Detection error: {str(e)}")
        return jsonify(error="Internal server error"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
