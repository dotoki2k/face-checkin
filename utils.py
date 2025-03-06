import os
import json
import string
import face_recognition


def encode_known_faces(known_faces_dir):
    """Encodes labeled face images from a specified directory.

    Args:
        known_faces_dir (str): Path to the folder containing labeled face images..

    Returns:
        tuple: A tuple containing:
            - list: Encoded face representations.
            - list: Corresponding face names.
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


def generate_excel_labels(n):
    """Get Excel-style column labels at the index n."""
    alphabet = list(string.ascii_uppercase)
    labels = []

    # Single letters (A-Z)
    labels.extend(alphabet)

    # Double letters (AA, AB, ..., ZZ)
    i = 0
    while len(labels) < n:
        for letter in alphabet:
            labels.append(alphabet[i] + letter)
            if len(labels) >= n:
                break
        i += 1

    return labels[n - 1]


def get_data_in_data_json():
    """
    Retrieves data from 'data.json' located in the 'credential' directory.

    If the file does not exist, it is created with an empty JSON object (`{}`),
    and an empty dictionary is returned. Otherwise, the function reads and
    returns the JSON content as a Python dictionary.

    Returns:
        dict: The parsed JSON data from 'data.json'. Returns an empty
              dictionary if the file is newly created or empty.
    """
    data_path = "./credential/data.json"
    if not os.path.exists(data_path):
        with open(data_path, "w") as file:
            file.write("{}")
        return {}
    with open(data_path, "r") as f:
        data = json.load(f)
    return data
