from pydantic import BaseModel
from typing import List
from datetime import date

class StudentCreate(BaseModel):
    name: str
    birthday: date
    email: str
    password: str
    face_vectors: List[List[float]]

class PayloadLogin(BaseModel):
    email: str
    password: str

class StudentUpdate(BaseModel):
    name: str
    email: str
    birthday: str
    role: str