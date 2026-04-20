from fastapi import APIRouter, Depends

from app.api.router.student import router as student_router
from app.api.router.attendance import router as attendance_router
from app.api.router.sepay import router as sepay_router
from app.api.router.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(student_router, prefix="/api")
api_router.include_router(attendance_router, prefix="/api")
api_router.include_router(sepay_router)
api_router.include_router(auth_router, prefix="/api")