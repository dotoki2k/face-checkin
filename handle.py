import cv2
import face_recognition
import numpy as np
import requests
import pytz
import gspread

from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials


WEBHOOK_URL = "https://discord.com/api/webhooks/1339288895250235523/NykXNA7pp_hBx3BSWp-tCVoufFCwLAmoEwauj1o_6G4tmBNz3bHwOxfYK4lJrYJaVWJO"
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = "./credential/gg_credential.json"
SPREADSHEET_ID = "1BZF7FL9cjJfipse_UTmZH4xq9ihxzLV6iTY9jwYQoOw"
VIETNAME_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

LIST_DETECTED = {}


def connect_google_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


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


def detect_and_identify_face(frame, known_encodings, known_names, name_mapped_to_excel):
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
                write_data_to_sheet(name, now, name_mapped_to_excel)
                send_message_to_discord(
                    f"{name.upper()} đã điểm danh lúc {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
        else:
            color = (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(
            frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
        )


def write_data_to_sheet(name, date_time, name_mapped_to_excel):
    col = name_mapped_to_excel.get(name, "")
    if not col:
        print(f"ERROR: can't write {name} to sheet.")
        return
    sheet = connect_google_sheets().sheet1
    today = date_time.strftime("%Y-%m-%d %H:%M")
    data = True

    sheet_data = sheet.col_values(1)
    if sheet_data[-1] == today:
        row_count = len(sheet_data)
    else:
        row_count = len(sheet_data) + 1

    sheet.update(f"A{row_count}", [[today]])
    sheet.update(f"{col}{row_count}", [[data]])
