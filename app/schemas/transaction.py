from pydantic import BaseModel

class GetTransaction(BaseModel):
    id: int
    amount: int
    gateway: str
    transaction_date: str
    account_number: str
    content: str
    code_student: str