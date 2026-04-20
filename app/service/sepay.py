from sqlalchemy.orm import Session
from datetime import datetime

from app.models.transaction import Transaction
from app.models.student import Student
from app.service.sendemail import send_email_confirm

def handler_transaction(data, db: Session):
    transaction_datetime = None
    if data.get("transactionDate"):
        try:
            transaction_datetime = datetime.strptime(
                data.get("transactionDate"), "%Y-%m-%d %H:%M:%S"
            )
        except (TypeError, ValueError):
            transaction_datetime = None

    existing = db.query(Transaction).filter(Transaction.id == data.get("id")).first()
    if existing:
        return {"status": "duplicate"}
    
    transfer_amount = data.get("transferAmount")
    if not isinstance(transfer_amount, (int, float)):
        raise ValueError(f"Invalid transferAmount: {transfer_amount}")

    amount_formatted = "{:,}".format(transfer_amount).replace(",", ".")

    content = data.get("content", "")
    code_student = content.split(" ")[0] if content else None

    student_email=None
    student_name=None
    if code_student:
        student = db.query(Student).filter(Student.code_student == code_student).first()
        if student: 
            student_email = student.email
            student_name = student.name

    if student_email:
        send_email_confirm(student_name, amount_formatted, student_email)

    transaction = Transaction(
        id=data.get("id"),
        amount=transfer_amount,
        gateway=data.get("gateway"),
        transaction_date=transaction_datetime,
        account_number=data.get("accountNumber"),
        content=content,
        code_student=code_student
    )

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
    except Exception as e:
        db.rollback()
        raise e
    
    return {"status": "ok"}

def get_data_transaction(db: Session):
    users = db.query(Transaction).all()
    return users