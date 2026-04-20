import os
from datetime import datetime
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.database import SessionLocal
from app.models.student import Student


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

def send_email_sendgrid(to_email: str, subject: str, html_content: str):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)

def send_email(to_email: str):
    now = datetime.now()
    deadline_day = now.day + 1
    subject = f"[PANDA TAEKWONDO] 🔔 THÔNG BÁO ĐÓNG HỌC PHÍ THÁNG {now.month:02d}/{now.year}"
    body = f"""
    <p><b>Kính gửi:</b> Quý Phụ huynh và các Võ sinh CLB Panda Taekwondo,</p>

    <p>Ban quản lý Câu lạc bộ Panda Taekwondo xin thông báo về việc hoàn tất học phí cho kỳ học 
    <b>Tháng {now.month:02d}/{now.year}</b>.</p>

    <p>Để đảm bảo việc sinh hoạt và tập luyện không bị gián đoạn, Quý phụ huynh và Võ sinh vui lòng hoàn tất học phí theo thông tin chi tiết dưới đây:</p>

    <ul style="margin-left:20px;">
        <li><b>Thời hạn nộp:</b> Trước ngày <b>{deadline_day:02d}/{now.month:02d}/{now.year}</b></li>
        <li><b>Kênh đóng học phí trực tuyến:</b> <a href="https://panda-taekwondo.vercel.app">panda-taekwondo.vercel.app</a></li>
    </ul>

    <p><b>Thông tin chuyển khoản trực tiếp:</b></p>
    <ul style="margin-left:10px;">
        <li><b>Ngân hàng:</b> Vietcombank</li>
        <li><b>Số tài khoản:</b> 1045032623</li>
        <li><b>Chủ tài khoản:</b> PHAM THANH NHAN</li>
        <li><b>Nội dung chuyển khoản:</b> [Mã võ sinh] [Tên võ sinh]</li>
    </ul>

    <p>Nếu có bất kỳ thắc mắc nào về học phí hoặc chương trình tập luyện, Quý phụ huynh vui lòng liên hệ trực tiếp với HLV Phạm Thanh Nhàn qua số điện thoại: 0338.287.804.</p>

    <p>Trân trọng cảm ơn sự đồng hành của Quý vị đối với CLB!<br>
    Ban quản lý của Panda Taekwondo</p>
    """

    send_email_sendgrid(to_email, subject, body)

def send_email_confirm(name: str, amount: int, to_email: str):
    now = datetime.now()
    deadline_day = now.day + 1
    subject = f"[PANDA TAEKWONDO] XÁC NHẬN HOÀN TẤT HỌC PHÍ THÁNG {now.month:02d}/{now.year} - VÕ SINH {name.upper()}"
    body = f"""
    <p><b>Kính gửi Quý Phụ huynh / Võ sinh,</b></p>

    <p>Ban quản lý Câu lạc bộ <b>Panda Taekwondo</b> xác nhận đã nhận được khoản thanh toán học phí tháng {now.month:02d}/{now.year} của võ sinh <b>{name.title()}</b>

    <p>Để đảm bảo việc sinh hoạt và tập luyện không bị gián đoạn, Quý phụ huynh và Võ sinh vui lòng hoàn tất học phí theo thông tin chi tiết dưới đây:</p>

    <ul style="margin-left:10px;">
        <li><b>Số tiền đã nhận: </b> {amount} VND</li>
        <li><b>Ngày thanh toán:</b> {deadline_day:02d}/{now.month:02d}/{now.year}</li>
        <li><b>Trạng thái: </b> Đã hoàn tất</li>
    </ul>

    <p>Cảm ơn Quý phụ huynh và Võ sinh đã hoàn tất học phí đúng hạn. Sự ủng hộ của Quý vị là động lực lớn để CLB tiếp tục duy trì môi trường tập luyện chất lượng cho các em.</p>

    <p>Chúc võ sinh có những giờ tập luyện hăng say và hiệu quả tại CLB!</p>
    <p><b>Trân trọng,</b></p>
    <p><b>HLV Phạm Thanh Nhàn</b></p>
    <p>CLB Panda Taekwondo</p>
    <p>SĐT: 0338.287.804</p>
    <p>Website: <a href="https://panda-taekwondo.vercel.app">panda-taekwondo.vercel.app</a></p>
    """

    send_email_sendgrid(to_email, subject, body)

def job_send_mail():
    db: Session = SessionLocal()
    students = db.query(Student).all()

    unique_emails = {stu.email for stu in students if stu.email}

    for email in unique_emails:
        send_email(email)

    print('job running...')
    db.close()