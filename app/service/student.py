import numpy as np

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.crud.student import find_duplicate_student
from app.utils import normalize_vector, get_cosine_similarity, generate_code_student, hash_password

def get_all(page: int, page_size: int, db: Session):
    skip = (page - 1) * page_size
    students = db.query(Student).offset(skip).limit(page_size).all()
    return {
        "page": page,
        "page_size": page_size,
        "data": [
            {
                "id": student.id,
                "code_student": student.code_student,
                "name": student.name,
                "birthday": student.birthday,
                "email": student.email,
                "role": student.role
            }
            for student in students
        ]
    }


def add_student(data: StudentCreate, db: Session):
    vectors_array = np.array(data.face_vectors)

    # ép về 2D nếu chỉ có 1 vector
    if vectors_array.ndim == 1:
        vectors_array = np.expand_dims(vectors_array, axis=0)

    # check hợp lệ
    if vectors_array.shape[0] < 1 or vectors_array.shape[1] != 128:
        raise HTTPException(
            status_code=400,
            detail="Cần ít nhất 1 mẫu khuôn mặt hợp lệ (128 chiều)."
        )

       
    normalized_vectors = np.array([
        normalize_vector(v) for v in vectors_array
    ])

    centroid = np.mean(normalized_vectors, axis=0)
    centroid = normalize_vector(centroid)

    existing_match = find_duplicate_student(
        db,
        centroid,
        threshold=0.95
    )

    if existing_match:
        student, score = existing_match
        return {
            "status": 409,
            "message": f"Khuôn mặt đã tồn tại ({score*100:.2f}%) - {student.name}"
        }
    
    code_student = generate_code_student(db)

    new_student = Student(
        name=data.name,
        code_student=code_student,
        birthday=data.birthday,
        email=data.email,
        password=hash_password(data.password),
        face_vector=centroid.tolist()
    )

    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ôi thôi chết! Tôi bị lỗi rồi")

    return {
        "status": 201,
        "message": "+ 1 Võ sinh",
        "data": {
            "id": new_student.id,
            "name": new_student.name,
            "birthday": new_student.birthday
        }
    }

def update(student_id: int, data: StudentUpdate, db: Session):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy con người này")
    
    update_data = data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)

    return {"message": "Võ sinh đã thay đổi"}

def delete(student_id: int, db: Session):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy con người này")
    
    db.delete(student)
    db.commit()

    return {"message": "Võ sinh đã bị bay màu"}