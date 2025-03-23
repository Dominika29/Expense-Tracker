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
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed: users.email' in str(e):
            flash('Email already exists', 'error')
        elif 'UNIQUE constraint failed: users.username' in str(e):
            flash('Username already exists', 'error')
        else:
            flash('An error occurred during registration.', 'error')
    finally:
        conn.close()
    return redirect(url_for('index'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        flash('Please log in to add an expense.', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    amount = float(request.form['amount'])
    description = request.form['description']
    category_id = request.form['category_id']
    date = request.form['date']
    new_category = request.form.get('new_category')
    
    conn = get_db_connection()

    try:
        if category_id == 'new' and new_category:

            existing_category = conn.execute(
                'SELECT id FROM categories WHERE name = ? AND user_id = ?',
                (new_category, user_id)
            ).fetchone()

            if existing_category:
                return redirect(url_for('dashboard'))
            
            cursor = conn.execute(
                'INSERT INTO categories (name, user_id) VALUES(?, ?)',
                (new_category, user_id)
            )
            conn.commit()
            category_id = cursor.lastrowid
            
        conn.execute(
            'INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)',
            (user_id, category_id, amount, description, date)
        )
        conn.commit()
        flash('Expense added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Invalid category or user', 'error')
    finally:
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    conn = get_db_connection()

    expenses = conn.execute('''
        SELECT expenses.id, expenses.amount, expenses.description, expenses.date, 
               categories.name AS category
        FROM expenses
        JOIN categories ON expenses.category_id = categories.id
        WHERE expenses.user_id = ?
        ORDER BY expenses.date ASC
    ''', (user_id,)).fetchall()
    
    categories = conn.execute('SELECT * FROM categories WHERE user_id = ?', (user_id,)).fetchall()
    print("Expenses:", expenses)
    print("Categories:", categories)

    conn.close()
    return render_template('dashboard.html',expenses=expenses, categories=categories)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        flash('Please log in to delete an expense.', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    conn = get_db_connection()

    try:
        expense = conn.execute(
            'SELECT * FROM expenses WHERE id = ? AND user_id = ?',
            (expense_id, user_id)
        ).fetchone()

        if expense:
            conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            conn.commit()
            flash('Expense deleted successfully!', 'success')
        else:
            flash('Expense not found or you do not have permission to delete it.', 'error')
    except sqlite3.Error as e:
        flash('An error occurred while deleting the expense.', 'error')
    finally:
        conn.close()

    return redirect(url_for('dashboard'))

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        flash('Please log in to edit an expense.', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    conn = get_db_connection()

    if request.method == 'POST':
        amount = request.form['amount']
        description = request.form['description']
        category_id = request.form['category_id']
        date = request.form['date']

        try:
            conn.execute(
                'UPDATE expenses SET amount = ?, description = ?, category_id = ?, date = ? WHERE id = ? AND user_id = ?',
                (amount, description, category_id, date, expense_id, user_id)
            )
            conn.commit()
            flash('Expense updated successfully!', 'success')
        except sqlite3.Error as e:
            flash('An error occurred while updating the expense.', 'error')
        finally:
            conn.close()

        return redirect(url_for('dashboard'))

    else:
        expense = conn.execute(
            'SELECT * FROM expenses WHERE id = ? AND user_id = ?',
            (expense_id, user_id)
        ).fetchone()

        categories = conn.execute('SELECT * FROM categories WHERE user_id = ?', (user_id,)).fetchall()
        conn.close()

        if expense:
            return render_template('edit_expense.html', expense=expense, categories=categories)
        else:
            flash('Expense not found or you do not have permission to edit it.', 'error')
            return redirect(url_for('dashboard'))
        
@app.route('/add_income', methods=['POST'])
def add_income():
    if 'user_id' not in session:
        flash('Please log in to add income.', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    amount = float(request.form['income_amount'])
    description = request.form['income_description']
    date = request.form['income_date']

    conn = get_db_connection()

    try:
        conn.execute(
            'INSERT INTO income (user_id, amount, description, date) VALUES (?, ?, ?, ?)',
            (user_id, amount, description, date)
        )
        conn.commit()
        flash('Income added successfully!', 'success')
    except sqlite3.Error as e:
        flash('An error occurred while adding income.', 'error')
    finally:
        conn.close()

    return redirect(url_for('dashboard'))


        
if __name__ == '__main__':
    app.run(debug=True)