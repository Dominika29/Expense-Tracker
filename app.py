import sqlite3
from flask import Flask, render_template

def get_db_connection():
    conn = sqlite3.connect('expense_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

@app.route("/")
def index():
    conn = get_db_connection()
    expenses = conn.execute('''
        SELECT expenses.id, expenses.amount, expenses.description, expenses.date, 
               categories.name AS category, users.username AS user
        FROM expenses
        JOIN categories ON expenses.category_id = categories.id
        JOIN users ON expenses.user_id = users.id
    ''').fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)