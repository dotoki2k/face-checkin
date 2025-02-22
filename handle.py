import cv2
import face_recognition
import numpy as np
import os
import requests
import pytz

from datetime import datetime
from sheet import write_data_to_sheet

WEBHOOK_URL = "https://discord.com/api/webhooks/1339288895250235523/NykXNA7pp_hBx3BSWp-tCVoufFCwLAmoEwauj1o_6G4tmBNz3bHwOxfYK4lJrYJaVWJO"
VIETNAME_TZ = pytz.timezone("Asia/Ho_Chi_Minh")
LIST_DETECTED = {}


def encode_known_faces(known_faces_dir):
    """Encode face image in folder

    Args:
        known_faces_dir (str): path folder contains image face labeled.

    Returns:
        tuple: tuple of list face encoded and list face name.
    """
    known_encodings = []
    known_names = []
    for filename in os.listdir(known_faces_dir):
        name, _ = os.path.splitext(filename)
        image_path = os.path.join(known_faces_dir, filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_encodings.append(encoding[0])
            known_names.append(name)
    return known_encodings, known_names


def send_message_to_discord(message):
    """Send message to discord.

    Args:
        message (str): message content.

    Returns:
        bool: return True if send the message successfully else False.
    """

    data = {"content": message}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        return True
    else:
        return False


def detect_and_identify_face(frame, known_encodings, known_names):
    """Detect and identify the face.

    Args:
        frame (CV2.image): frame image in CV2.
        known_encodings (list): list face encoded.
        known_names (list): list the name of the face encoded..
    """

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    obj_datetime = datetime.now(VIETNAME_TZ)
    # TODO write the face identify to file.
    date_now = obj_datetime.strftime("%Y-%m-%d %H:%M")
    if LIST_DETECTED.get(date_now, None) is None:
        LIST_DETECTED[date_now] = []
    for (top, right, bottom, left), face_encoding in zip(
        face_locations, face_encodings
    ):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "unknown"

        # find the best match
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = (
            np.argmin(face_distances) if len(face_distances) > 0 else None
        )

        if best_match_index is not None and matches[best_match_index]:
            name = known_names[best_match_index]

        # draw name
        color = (0, 255, 0) if name != "unknown" else (0, 0, 255)
        if name != "unknown":
            color = (0, 255, 0)
            if name not in LIST_DETECTED.get(date_now):
                LIST_DETECTED[date_now].append(name)
                now = datetime.now(VIETNAME_TZ)
                write_data_to_sheet(name, now)
                send_message_to_discord(
                    f"{name.upper()} đã điểm danh lúc {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
        else:
            color = (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(
            frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
        )
