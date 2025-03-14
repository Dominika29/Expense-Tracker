import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect('expense_tracker.db')


with open('expense_log.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

hashed_password = generate_password_hash('hashed_password_123')

cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            ('admin', hashed_password, 'admin@example.com'))

user_id = cur.lastrowid

cur.execute("INSERT INTO categories (name, user_id) VALUES (?, ?)",
            ('Jedzenie', user_id))
cur.execute("INSERT INTO categories (name, user_id) VALUES (?, ?)",
            ('Transport', user_id))
cur.execute("INSERT INTO categories (name, user_id) VALUES (?, ?)",
            ('Rozrywka', user_id))

category_food_id = cur.lastrowid - 2
category_transport_id = cur.lastrowid - 1
category_entertainment_id = cur.lastrowid 

cur.execute("INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, category_food_id, 50.00, 'Zakupy w Biedronce', '2023-10-01'))
cur.execute("INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, category_transport_id, 20.00, 'Bilet autobusowy', '2023-10-02'))

connection.commit()
connection.close()

print("Database initialized successfully!")