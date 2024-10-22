from app import app, db, User

if __name__ == "__main__":
    with app.app_context():
        # Tạo lại cơ sở dữ liệu (nếu cần)
        db.create_all()

        # Kiểm tra xem người dùng 'admin' đã tồn tại chưa
        if not User.query.filter_by(username='admin').first():
            # Thêm người dùng mới với tên đăng nhập là 'admin' và mật khẩu là 'admin@123'
            admin_user = User(username='admin')
            admin_user.set_password('admin@123')
            db.session.add(admin_user)
            db.session.commit()
            print("Người dùng 'admin' đã được thêm vào cơ sở dữ liệu với mật khẩu 'admin@123'.")

    app.run(host='0.0.0.0', port=5000, debug=True)
