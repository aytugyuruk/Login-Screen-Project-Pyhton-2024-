from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session
from models import Base, User, engine, SessionLocal
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_users(db: Session):
    return db.query(User).all()

@app.route('/')
def home():
    return redirect(url_for('user_login'))

@app.route('/user-login')
def user_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash('Username and Password are required!')
        return redirect(url_for('user_login'))
    
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    
    if user and user.password == password:
        return redirect(url_for('success'))
    else:
        flash('Invalid username or password!')
        return redirect(url_for('error'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/forgot-password')
def forgot_password():
    return "Forgot Password Page"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:
            flash('All fields are required!')
            return redirect(url_for('register'))
        
        db = next(get_db())
        user = db.query(User).filter(User.username == username).first()

        if user:
            flash('Username already exists!')
            return redirect(url_for('register'))
        
        # Kullanıcı bilgilerini veritabanına düz metin olarak yaz
        new_user = User(username=username, email=email, password=password)
        db.add(new_user)
        db.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('user_login'))

    return render_template('register.html')

@app.route('/view-users')
def view_users():
    db = next(get_db())
    users = load_users(db)
    return render_template('view_users.html', users=users)

@app.route('/reset-users', methods=['POST'])
def reset_users():
    db = next(get_db())
    try:
        num_rows_deleted = db.query(User).delete()
        db.commit()
        flash(f"Deleted {num_rows_deleted} users.")
    except Exception as e:
        db.rollback()
        flash(f"An error occurred while resetting users: {e}")
    return redirect(url_for('view_users'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
