from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id=Column(Integer, primary_key=True, index=True)
    code_student=Column(String, nullable=False)
    name=Column(String, nullable=False)
    birthday=Column(Date, nullable=False)
    email=Column(String, nullable=False)
    password=Column(String, nullable=False)
    role=Column(String, nullable=False, default='user')
    face_vector=Column(ARRAY(Float), nullable=False)
    attendance_logs = relationship(
        "AttendanceLog",
        back_populates="student",
        cascade="all, delete"
    )