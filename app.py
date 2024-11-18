from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_mail import Mail, Message
from datetime import datetime
import os
import tempfile
import openpyxl
from unidecode import unidecode
from flask_migrate import Migrate
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///violations.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'trafficviolations248@gmail.com'
app.config['MAIL_PASSWORD'] = 'pvaw anaq fkjy irpq'
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    violation = db.Column(db.String(200), nullable=False)
    violation_date = db.Column(db.DateTime, nullable=False)
    added_by = db.Column(db.String(150), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            msg = Message('Your Password', sender='your-email@gmail.com', recipients=['maiphuong7284@gmail.com'])
            msg.body = f"Your password is: {user.password}"
            mail.send(msg)
            return 'An email with your password has been sent.'
        return 'User not found.'
    return render_template('forgot_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/users')
@login_required
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users, current_user=current_user)

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('add_user.html')

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get(id)
    if request.method == 'POST':
        password = request.form['password']
        user.set_password(password)
        db.session.commit()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/')
@login_required
def index():
    search = request.args.get('search')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 50

    if search:
        search = unidecode(search).lower()
        violations_query = Violation.query.filter_by(is_deleted=False).all()
        violations = [v for v in violations_query if search in unidecode(v.name).lower() or search in unidecode(v.license_plate).lower()]
    else:
        violations = Violation.query.filter_by(is_deleted=False).all()

    total = len(violations)
    start = (page - 1) * per_page
    end = start + per_page
    violations_paginated = violations[start:end]

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')

    return render_template('index.html', violations=violations_paginated, pagination=pagination, search=search)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_violation():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        address = request.form['address']
        license_plate = request.form['license_plate']
        violations = request.form.getlist('violation')
        violation_date = datetime.strptime(request.form['violation_date'], '%Y-%m-%dT%H:%M')
        
        print(f"Received data: {name}, {birth_date}, {address}, {license_plate}, {violations}, {violation_date}")
        
        for violation in violations:
            new_violation = Violation(
                name=name,
                birth_date=birth_date,
                address=address,
                license_plate=license_plate,
                violation=violation,
                violation_date=violation_date,
                added_by=current_user.username
            )
            db.session.add(new_violation)
        
        db.session.commit()
        flash('Thêm vi phạm thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_violation(id):
    violation = Violation.query.get(id)
    if violation:
        violation.is_deleted = True
        db.session.commit()
        flash('Xóa vi phạm thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/export_excel')
@login_required
def export_excel():
    try:
        violations = Violation.query.filter_by(is_deleted=False).all()
        data = [{
            'Họ tên': v.name,
            'Ngày tháng năm sinh': v.birth_date,
            'Địa chỉ': v.address,
            'Biển số xe': v.license_plate,
            'Lỗi vi phạm': v.violation,
            'Ngày giờ vi phạm': v.violation_date,
            'Người nhập': v.added_by
        } for v in violations]

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            file_path = tmp.name
            workbook = openpyxl.Workbook()
            sheet = workbook.active

            # Write headers
            headers = ['Họ tên', 'Ngày tháng năm sinh', 'Địa chỉ', 'Biển số xe', 'Lỗi vi phạm', 'Ngày giờ vi phạm', 'Người nhập']
            sheet.append(headers)

            # Write data
            for row_data in data:
                sheet.append([
                    row_data['Họ tên'],
                    row_data['Ngày tháng năm sinh'].strftime('%Y-%m-%d'),
                    row_data['Địa chỉ'],
                    row_data['Biển số xe'],
                    row_data['Lỗi vi phạm'],
                    row_data['Ngày giờ vi phạm'].strftime('%Y-%m-%d %H:%M:%S'),
                    row_data['Người nhập']
                ])

            workbook.save(file_path)

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Thêm người dùng mặc định nếu chưa tồn tại
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin')
            admin_user.set_password('admin@123')
            db.session.add(admin_user)
            db.session.commit()
            print("Người dùng 'admin' đã được thêm vào cơ sở dữ liệu với mật khẩu 'admin@123'.")
    app.run(host='0.0.0.0', port=5000, debug=True)