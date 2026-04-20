from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.schemas import AttendanceRequest, MonthlyAttendanceResponse
from app.service import get_monthly_attendance, attendance_student, get_current_user

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import face_recognition
import io
import numpy as np

from app.service.auth import get_current_user
from supabase_client import supabase

router = APIRouter(prefix="/attendance", tags=["Attendance"], dependencies=[Depends(get_current_user)])


@router.post("/check-in")
async def check_in(
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    try:
        contents = await file.read()

        # đọc ảnh
        image = face_recognition.load_image_file(io.BytesIO(contents))

        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            return {"message": "❌ Không thấy khuôn mặt"}

        new_face = encodings[0]

        # 🔥 lấy tất cả user từ supabase
        users = supabase.table("students").select("*").execute().data

        for u in users:
            stored_vector = np.array(u["face_vector"])

            # so sánh
            match = face_recognition.compare_faces([stored_vector], new_face)[0]

            if match:
                return {"message": f"✅ Xin chào {u['name']}"}

        return {"message": "❌ Không nhận diện được - mời điểm danh lại"}

    except Exception as e:
        print(e)
        raise HTTPException(500, "Lỗi server")
def check_attendance(data: AttendanceRequest, db: Session = Depends(get_db)):
    return attendance_student(data, db)

@router.get("/month", response_model = MonthlyAttendanceResponse)
def monthly_attendance(month: int, year: int, db: Session = Depends(get_db)):
    return get_monthly_attendance(db, month, year)