from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, UploadFile, File
from app.service.face import encode_face, save_face, verify_face

from app.api import api_router
from app.service.sendemail import job_send_mail

app = FastAPI()

scheduler = BackgroundScheduler()

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(job_send_mail, 'cron', day=5, hour=8, minute=0)
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serve static files
app.mount("/", StaticFiles(directory=".", html=True), name="static")

@app.post("/register-face/{user_id}")
async def register_face(user_id: str, file: UploadFile = File(...)):
    image_bytes = await file.read()

    encoding = encode_face(image_bytes)

    if encoding is None:
        return {"error": "Không nhận diện được khuôn mặt"}

    save_face(user_id, encoding)

    return {"message": "Đăng ký khuôn mặt thành công"}

@app.post("/attendance/{user_id}")
async def attendance(user_id: str, file: UploadFile = File(...)):
    image_bytes = await file.read()

    new_encoding = encode_face(image_bytes)

    if new_encoding is None:
        return {"message": "Không thấy khuôn mặt"}

    is_match = verify_face(user_id, new_encoding)

    if is_match:
        return {"message": "✅ Điểm danh thành công"}
    else:
        return {"message": "❌ Sai người"}

