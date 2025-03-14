import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    conn = sqlite3.connect('expense_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password', 'error')
        return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    new_username = request.form['new_username']
    new_password = request.form['new_password']
    new_email = request.form['new_email']
    
    hashed_password = generate_password_hash(new_password)
    
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
            (new_username, hashed_password, new_email)
        )
        conn.commit()
        flash('Registration successful!', 'success')
    except sqlite3.IntegrityError:
        flash('Username or email already exists', 'error')
    finally:
        conn.close()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)