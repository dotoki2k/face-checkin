import cv2
import face_recognition
import numpy as np
import requests
import pytz
import gspread
import logging

from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from utils import generate_excel_labels

WEBHOOK_URL = ""
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = "./credential/gg_credential.json"
SPREADSHEET_ID = "1BZF7FL9cjJfipse_UTmZH4xq9ihxzLV6iTY9jwYQoOw"
VIETNAME_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

LIST_DETECTED = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def connect_google_sheets():
    """Connect to Google Spreadsheet.

    Returns:
        Spreadsheet: a :class:`~gspread.models.Spreadsheet` instance.
    """
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
                write_data_to_sheet(name, now, known_names)
                send_message_to_discord(
                    f"{name.upper()} đã điểm danh lúc {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info(
                    f"{name.upper()} counted at: ({now.strftime('%Y-%m-%d %H:%M:%S')})"
                )
        else:
            color = (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(
            frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
        )


def write_data_to_sheet(name, date_time, known_names):
    """Writes data to a Google Spreadsheet.

    Args:
        name (str): The name of the identified person.
        date_time (datetime): The date and time of identification.
        known_names (list): A list of known names.
    """
    try:
        index = known_names.index(name) + 1
    except ValueError:
        index = None
    if not index:
        print(f"ERROR: can't write {name} to sheet.")
        return
    sheet_id = "dev1"
    sheet = connect_google_sheets().worksheet(sheet_id)
    today = date_time.strftime("%Y-%m-%d %H:%M")
    data = True
    date_row = sheet.row_values(1)
    if not date_row:
        col_index = 2
    elif date_row[-1] == today:
        col_index = len(date_row)
    else:
        col_index = len(date_row) + 1
    column_character = generate_excel_labels(col_index)
    try:
        sheet.update(f"A{index}", [[name]])
        sheet.update(f"{column_character}1", [[today]])
        sheet.update(f"{column_character}{index}", [[data]])
    except Exception as ex:
        if "exceeds gird limits" in str(ex).lower():
            # Add 5 columns and try writing data into the sheet again.
            sheet.add_cols(5)
            sheet.update(f"{column_character}1", [[today]])
            sheet.update(f"{column_character}{index}", [[data]])
        logger.error("Got an error while write data into sheet. Check the log below")
        logger.exception(str(ex))
