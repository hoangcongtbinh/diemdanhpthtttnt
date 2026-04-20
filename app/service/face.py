import face_recognition
import numpy as np
import pickle
import os
from typing import Optional

FACE_DIR = "face_data"


# tạo folder nếu chưa có
if not os.path.exists(FACE_DIR):
    os.makedirs(FACE_DIR, exist_ok=True)


# =========================
# ENCODE
# =========================
def encode_face(image_bytes: bytes) -> Optional[np.ndarray]:
    import io
    from PIL import Image

    image = Image.open(io.BytesIO(image_bytes))
    image = np.array(image)

    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return None

    return encodings[0]


# =========================
# SAVE FACE
# =========================
def save_face(user_id: str, encoding: np.ndarray):
    path = os.path.join(FACE_DIR, f"{user_id}.pkl")

    with open(path, "wb") as f:
        pickle.dump(encoding, f)


# =========================
# LOAD FACE
# =========================
def load_face(user_id: str) -> Optional[np.ndarray]:
    path = os.path.join(FACE_DIR, f"{user_id}.pkl")

    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return pickle.load(f)


# =========================
# COMPARE 1 USER
# =========================
def verify_face(user_id: str, new_encoding: np.ndarray) -> bool:
    known_encoding = load_face(user_id)

    if known_encoding is None:
        return False

    result = face_recognition.compare_faces([known_encoding], new_encoding)
    return result[0]


# =========================
# FIND MATCH (MULTI USER)
# =========================
def find_matching_user(new_encoding: np.ndarray) -> Optional[str]:
    for file in os.listdir(FACE_DIR):
        path = os.path.join(FACE_DIR, file)

        with open(path, "rb") as f:
            known_encoding = pickle.load(f)

        match = face_recognition.compare_faces([known_encoding], new_encoding)

        if match[0]:
            return file.replace(".pkl", "")

    return None