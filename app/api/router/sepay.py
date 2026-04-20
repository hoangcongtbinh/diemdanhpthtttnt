from fastapi import APIRouter, Request
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.service.sepay import handler_transaction, get_data_transaction
from app.service.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/webhook", tags=["Webhook"])

@router.post("/sepay")
async def sepay_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    return handler_transaction(data, db)

@router.get("/transaction", dependencies=[Depends(get_current_user), Depends(get_current_admin)])
def get_transaction(db: Session = Depends(get_db)):
    return get_data_transaction(db)