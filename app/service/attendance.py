import calendar
import numpy as np
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from collections import defaultdict
from fastapi import HTTPException

from app.models.attendance import AttendanceLog
from app.models.student import Student
from app.models.transaction import Transaction
from app.schemas.attendance import AttendanceRequest
from app.crud.student import find_best_match_attendance
from app.utils import normalize_vector



def get_monthly_attendance(db: Session, month: int, year: int, schedule_days=[ 1, 3, 6 ]):
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    valid_students = (
        db.query(Student)
        .join(Transaction, Transaction.code_student == Student.code_student)
        .filter(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        )
        .all()
    )

    logs = db.query(AttendanceLog).filter(
        AttendanceLog.checkin_time >= start_date,
        AttendanceLog.checkin_time < end_date
    ).all()

    attendance_map = defaultdict(set)
    for log in logs:
        attendance_map[log.student_id].add(log.checkin_time.date())

    num_days = calendar.monthrange(year, month)[1]
    schedule_dates = [
        date(year, month, d)
        for d in range(1, num_days+1)
        if date(year, month, d).weekday() in schedule_days
    ]

    today = date.today()

    result = []
    for stu in valid_students:
        attended_days = attendance_map.get(stu.id, set())
        attended_count = sum(1 for d in schedule_dates if d in attended_days)
        missed_count = len([d for d in schedule_dates if d < today and d not in attended_days])
        percent = round(attended_count / len(schedule_dates) * 100, 2) if schedule_dates else 0

        details = {}
        for d in schedule_dates:
            if d in attended_days:
                details[str(d)] = "present"
            elif d < today:
                details[str(d)] = "absent"
            else:
                details[str(d)] = "upcoming"

        result.append({
            "student_id": stu.id,
            "code_student": stu.code_student,
            "name": stu.name,
            "attended": attended_count,
            "missed": missed_count,
            "attendance_rate": percent,
            "details": details
        })

    return {
        "total_classes": len(schedule_dates),
        "data": result
    }


def attendance_student(data: AttendanceRequest, db: Session):
    vectors_array = np.array(data.face_vectors)

    if len(vectors_array) < 3 or vectors_array.shape[1] != 128:
        raise HTTPException(
            status_code=400,
            detail="Vector không hợp lệ."
        )

    normalized_vectors = [
        normalize_vector(v) for v in vectors_array
    ]

    result = find_best_match_attendance(
        db,
        normalized_vectors,
        threshold=0.85
    )

    if result is None:
        return {
            "status": 404,
            "message": "Không nhận diện được khuôn mặt. Vui lòng thử lại!",
            "data": None
        }

    student, score = result

    today = date.today()
    start_month = date(today.year, today.month, 1)
    if today.month == 12:
        end_month = date(today.year + 1, 1, 1)
    else:
        end_month = date(today.year, today.month + 1, 1)

    transaction = db.query(Transaction).filter(
        Transaction.code_student == student.code_student,
        Transaction.transaction_date >= start_month,
        Transaction.transaction_date < end_month
    ).first()


    if not transaction:
        return {
            "status": 403,
            "message": "Bạn chưa đóng học phí trong tháng này.",
            "data": {"code_student": student.code_student, "name": student.name}
        }

    last_log = db.query(AttendanceLog).filter(
        AttendanceLog.student_id == student.id,
        func.date(AttendanceLog.checkin_time) == today
    ).first()

    if last_log:
        return {
            "status": 202,
            "message": f"Võ sinh {student.name} đã điểm danh hôm nay rồi.",
            "data": {"id": student.id, "name": student.name}
        }

    new_log = AttendanceLog(student_id=student.id)

    try:
        db.add(new_log)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ôi thôi chết! Tôi bị lỗi rồi")

    return {
        "status": 200,
        "message": f"Điểm danh thành công! Xin chào {student.name}",
        "data": {
            "id": student.id,
            "name": student.name,
            "similarity": float(score)
        }
    }