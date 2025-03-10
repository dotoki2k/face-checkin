# app.py
import cv2
import json
import logging
import base64
import numpy as np

from flasgger import Swagger
from utils import encode_known_faces, get_data_in_data_json
from handler import detect_and_identify_face
from logger.logger_config import setup_logging
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
swagger = Swagger(app)
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
    """Process the image."""
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


@app.route("/config", methods=["POST"])
def config_data():
    """
    Config data for Face-Checkin application.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
            type: object
            properties:
                discord_webhook:
                    type: string
                    description: The Discord webhook link to send notifications.
                google_spreadsheet:
                    type: string
                    description: The Google spreadsheet link to write record.
    responses:
      200:
        description: Configured the data for Face-Checkin application.
      400:
        description: Invalid input (e.g., no file provided)
      500:
        description: Internal server error
    """
    raw_data = request.json
    webhook = raw_data.get("discord_webhook", None)
    sheet_id = raw_data.get("google_spreadsheet", None)
    file_data = get_data_in_data_json()
    if webhook:
        file_data["discord_webhook"] = webhook
    if sheet_id:
        file_data["google_spreadsheet"] = sheet_id

    with open("./credential/data.json", "w") as file:
        json.dump(file_data, file, indent=4)

    return jsonify("Update Successful"), 200


@app.route("/showdata", methods=["GET"])
def show_data():
    """
    Get data the roll call log from file.
    ---
    responses:
      200:
        description: Successfully.
      400:
        description: Invalid input (e.g., no file provided).
      500:
        description: Internal server error.
    """
    with open("./logs/roll_call.txt", "r", encoding="utf-8") as file:
        data = file.read()

    return jsonify({"count": len(data), "entries": data}), 200


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Face-checkin is starting..")
    app.run(host="0.0.0.0", port=5000)
