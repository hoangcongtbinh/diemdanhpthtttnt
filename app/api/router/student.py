from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi import UploadFile, File, Form, HTTPException
from app.api.deps import get_db
from app.schemas.student import StudentCreate, StudentUpdate
from app.models.student import Student
from app.service.auth import get_current_admin, get_current_user
from app.service.student import get_all, add_student, update, delete
from app.utils import hash_password


import face_recognition
import io
from supabase_client import supabase 

router = APIRouter(prefix="/students", tags=["Students"])

#  API mới: đăng ký + face vector
@router.post("/register-face")
async def register_face(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # đọc ảnh
        contents = await file.read()

        # load ảnh
        image = face_recognition.load_image_file(io.BytesIO(contents))

        # lấy vector 128 chiều
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            raise HTTPException(400, "Không nhận diện được khuôn mặt")

        face_vector = encodings[0].tolist()

        # 🔥 lưu vào Supabase
        res = supabase.table("students").insert({
            "name": name,
            "email": email,
            "password": hash_password(password),
            "face_vector": face_vector
        }).execute()

        print("INSERT:", res)

        return {"message": "Đăng ký thành công"}

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(500, str(e))

@router.get("/")
def get_student(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    return get_all(page, page_size, db)

@router.post("/create")
def register_student(data: StudentCreate, db: Session = Depends(get_db)):
    return add_student(data, db)

@router.put("/{student_id}")
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    return update(student_id, data, db)

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    return delete(student_id, db)