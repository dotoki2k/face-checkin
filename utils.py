import os
import string
import face_recognition


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


def generate_excel_labels(n):
    """Generate Excel-style column labels up to the required number n."""
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
