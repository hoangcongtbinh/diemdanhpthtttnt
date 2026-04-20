from sqlalchemy import Column, Integer, String, Date

from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id=Column(Integer, primary_key=True, index=True)
    amount=Column(Integer)
    gateway=Column(String)
    transaction_date=Column(Date)
    account_number=Column(String)
    content=Column(String)
    code_student=Column(String)