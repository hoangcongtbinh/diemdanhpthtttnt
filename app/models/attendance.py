from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import pytz

def get_vn_time():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    checkin_time = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="attendance_logs")