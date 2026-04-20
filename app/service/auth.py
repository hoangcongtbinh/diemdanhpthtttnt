from jose import jwt, JWTError
from fastapi import HTTPException, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.schemas.student import PayloadLogin
from app.models.student import Student
from app.utils import verify_password

SECRET_KEY="secret"
ALGORITHM="HS256"

security = HTTPBearer()

def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(hours=1)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
    
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token:
        return HTTPException(401, "Bạn không có quyền truy cập, Hãy đăng nhập")
    payload = decode_token(token)
    return payload

def get_current_admin(user = Depends(get_current_user)):
    if(user.get('role') != 'admin'):
        raise HTTPException(403, 'Admin only')
    return user

def signin(data: PayloadLogin, db: Session, response: Response):
    if not data.email or not data.password:
        raise HTTPException(400, "Missing email or password")

    student = db.query(Student).filter(Student.email == data.email).first()

    if not student or not verify_password(data.password, student.password):
        raise HTTPException(401, "Invalid email or password")

    token = create_token({
        "sub": student.name,
        "role": student.role
    })

    return {
        "message": "Đăng nhập thành công",
        "access_token": token,
        "user": {
            "code_student": student.code_student,
            "name": student.name,
            "email": student.email,
            "role": student.role
        }
    }

def signout(response: Response):
    response.delete_cookie(
        key="access_token",
        secure=True,
        samesite="none",
    )
    return {"message": "Đăng xuất thành công"}