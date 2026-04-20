from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.student import PayloadLogin
from app.service.auth import signin, signout

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(data: PayloadLogin, response: Response, db: Session = Depends(get_db)):
    return signin(data, db, response)

@router.post("/logout")
def logout(response: Response):
    return signout(response)