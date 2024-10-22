from app import app, db, Violation
from datetime import datetime

# Tạo ngữ cảnh ứng dụng
with app.app_context():
    # Thêm bản ghi mới vào bảng violation
    new_violation = Violation(
        name="Nguyễn Văn A",
        birth_date=datetime.strptime("1990-01-01", "%Y-%m-%d").date(),
        address="123 Đường ABC",
        license_plate="79H-123456",
        violation="Không Đội Mũ Bảo Hiểm",
        violation_date=datetime.strptime("2024-10-22 10:00:00", "%Y-%m-%d %H:%M:%S")
    )
    db.session.add(new_violation)
    db.session.commit()

print("Bản ghi mới đã được thêm vào cơ sở dữ liệu.")
