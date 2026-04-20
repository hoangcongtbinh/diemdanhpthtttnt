import numpy as np
import hashlib
import bcrypt
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.models.student import Student


def _prepare_password_for_bcrypt(password: str) -> str:
    # Bcrypt only supports 72 bytes, so we pre-hash to a fixed-length string.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def cosine_similarity(a, b):
    a=np.array(a)
    b=np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_cosine_similarity(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    
    dot_product = np.dot(v1, v2)
    
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return dot_product / (norm_v1 * norm_v2)

def get_week_of_moth(dt):
    return (dt.day - 1) // 7 + 1

def normalize_vector(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def generate_code_student(db: Session):
    last = db.query(Student).order_by(Student.id.desc()).first()
    if not last:
        return "SV001"
    num = int(last.code_student[2:])
    return f"SV{num+1:03d}"

def hash_password(password: str):
    prepared_password = _prepare_password_for_bcrypt(password).encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(prepared_password, salt).decode("utf-8")

def verify_password(plain, hashed):
    prepared_password = _prepare_password_for_bcrypt(plain).encode("utf-8")
    return bcrypt.checkpw(prepared_password, hashed.encode("utf-8"))
    