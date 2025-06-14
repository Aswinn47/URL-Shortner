from flask import Flask, render_template, request, redirect, url_for, session, flash
import re
import sqlite3
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # URL table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
            original TEXT NOT NULL,
            short TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# ---------------- USER CLASS ----------------
class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(id=user[0], name=user[1], email=user[2], password=user[3])
    return None

# ---------------- ROUTES ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # 1. Check if user already exists first
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = c.fetchone()
        conn.close()

        if existing_user:
            flash('Account already exists. Please log in.', 'warning')
            return redirect(url_for('register'))

        # 2. Then validate password
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password):
            flash("Password must be at least 6 characters long and include both letters and numbers.", "warning")
            return redirect(url_for('register'))

        # 3. Save new user
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                  (full_name, email, hashed_password))
        conn.commit()
        conn.close()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            user_obj = User(id=user[0], name=user[1], email=user[2], password=user[3])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')  # 👈 Only shown on login page
            return redirect(url_for('login'))

    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO urls (user_id, original, short) VALUES (?, ?, ?)", (current_user.id, original_url, short_id))
        conn.commit()
        conn.close()

        return render_template('result.html', short_url=request.host_url + short_id)

    return render_template('index.html')

@app.route('/<short_id>')
def redirect_url(short_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT original FROM urls WHERE short = ?", (short_id,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return "<h1>URL not found</h1>", 404

# ------------- MAIN --------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
