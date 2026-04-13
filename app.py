import os
import math
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
                        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        subject_name TEXT NOT NULL,
                        total_classes INTEGER NOT NULL DEFAULT 0,
                        attended_classes INTEGER NOT NULL DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    conn.commit()
    conn.close()

# Initialize automatically
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    flash("Registration is disabled. Please use the teacher login.", "warning")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hardcoded teacher login
        if email == 'gaurav443201' and password == '443201':
            session['user_id'] = 1
            session['user_name'] = 'Gaurav (Teacher)'
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials! Use Username: gaurav443201, Password: 443201", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    subjects = []
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects WHERE user_id = ?", (user_id,))
        subjects_rows = cursor.fetchall()
        subjects = [dict(row) for row in subjects_rows]
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals():
            conn.close()
            
    # Process attendance logic
    overall_total = 0
    overall_attended = 0
    
    for sub in subjects:
        total = sub['total_classes']
        attended = sub['attended_classes']
        overall_total += total
        overall_attended += attended
        
        if total == 0:
            sub['attendance_percent'] = 0.0
            sub['status'] = 'gray'
            sub['message'] = "No classes yet."
            sub['bunk_count'] = 0
            sub['recover_count'] = 0
        else:
            percent = (attended / total) * 100
            sub['attendance_percent'] = round(percent, 2)
            
            if percent > 75:
                sub['status'] = 'green'
                x = math.floor((attended - 0.75 * total) / 0.75)
                sub['message'] = f"You can bunk {x} classes"
                sub['bunk_count'] = x
            elif percent == 75.0:
                sub['status'] = 'yellow'
                sub['message'] = "You are exactly at 75%. Don't bunk!"
                sub['bunk_count'] = 0
            else:
                sub['status'] = 'red'
                y = math.ceil(3 * total - 4 * attended)
                sub['message'] = f"Attend next {y} classes to reach safe level"
                sub['recover_count'] = y
                
    overall_percent = round((overall_attended / overall_total * 100), 2) if overall_total > 0 else 0.0
    
    return render_template('dashboard.html', subjects=subjects, overall_percent=overall_percent)

@app.route('/subject/add', methods=['POST'])
@login_required
def add_subject():
    name = request.form.get('subject_name')
    total = int(request.form.get('total_classes', 0))
    attended = int(request.form.get('attended_classes', 0))
    user_id = session['user_id']
    
    if not name:
        flash("Subject name is required.", "danger")
        return redirect(url_for('dashboard'))
        
    if attended > total:
        flash("Attended classes cannot be greater than total classes.", "danger")
        return redirect(url_for('dashboard'))
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (user_id, subject_name, total_classes, attended_classes) VALUES (?, ?, ?, ?)",
                       (user_id, name, total, attended))
        conn.commit()
        flash("Subject added successfully!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('dashboard'))

@app.route('/subject/edit/<int:subject_id>', methods=['POST'])
@login_required
def edit_subject(subject_id):
    name = request.form.get('subject_name')
    total = int(request.form.get('total_classes', 0))
    attended = int(request.form.get('attended_classes', 0))
    user_id = session['user_id']
    
    if attended > total:
        flash("Attended classes cannot be greater than total classes.", "danger")
        return redirect(url_for('dashboard'))
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE subjects SET subject_name=?, total_classes=?, attended_classes=? WHERE subject_id=? AND user_id=?",
                       (name, total, attended, subject_id, user_id))
        conn.commit()
        flash("Subject updated!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('dashboard'))

@app.route('/subject/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    user_id = session['user_id']
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE subject_id=? AND user_id=?", (subject_id, user_id))
        conn.commit()
        flash("Subject deleted!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('dashboard'))

@app.route('/subject/quick_add/<int:subject_id>/<action>', methods=['POST'])
@login_required
def quick_action(subject_id, action):
    user_id = session['user_id']
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        if action == 'attend':
            cursor.execute("UPDATE subjects SET total_classes=total_classes+1, attended_classes=attended_classes+1 WHERE subject_id=? AND user_id=?", (subject_id, user_id))
        elif action == 'bunk':
            cursor.execute("UPDATE subjects SET total_classes=total_classes+1 WHERE subject_id=? AND user_id=?", (subject_id, user_id))
        conn.commit()
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals():
            conn.close()
            
    return redirect(url_for('dashboard'))
    
@app.route('/api/chart_data')
@login_required
def chart_data():
    user_id = session['user_id']
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT subject_name, total_classes, attended_classes FROM subjects WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        subjects_data = [{"subject_name": row["subject_name"], "total_classes": row["total_classes"], "attended_classes": row["attended_classes"]} for row in rows]
        
        labels = []
        attendance_rates = []
        for sub in subjects_data:
            labels.append(sub['subject_name'])
            perc = (sub['attended_classes'] / sub['total_classes'] * 100) if sub['total_classes'] > 0 else 0
            attendance_rates.append(round(perc, 2))
            
        return jsonify({'labels': labels, 'data': attendance_rates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
