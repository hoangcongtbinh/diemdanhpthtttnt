from sqlalchemy.orm import Session
from app.models.student import Student
from app.utils import get_cosine_similarity
import numpy as np

def find_duplicate_student(db: Session, new_vector: np.ndarray, threshold=0.95):

    students = db.query(Student).all()
    if not students:
        return None

    best_student = None
    best_score = -1

    for stu in students:
        stu_vector = np.array(stu.face_vector)
        score = float(get_cosine_similarity(new_vector, stu_vector))

        if score > best_score:
            best_score = score
            best_student = stu

    if best_score < threshold:
        return None

    return best_student, best_score

def create_student(db: Session):
    code = generate_code_student()

def find_best_match_attendance(db: Session, new_vectors, threshold=0.85):

    students = db.query(Student).all()
    if not students:
        return None

    best_student = None
    best_score = -1


    for stu in students:
        stu_vector = np.array(stu.face_vector)

        scores = [
            get_cosine_similarity(v, stu_vector)
            for v in new_vectors
        ]

        avg_score = np.mean(scores)

        if avg_score > best_score:
            best_score = avg_score
            best_student = stu

    if best_score < threshold:
        return None

    return best_student, best_score
