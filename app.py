import os
import math
import mysql.connector
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')

# MySQL Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '443201'), 
    'database': os.environ.get('DB_NAME', 'bunk_manager'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hardcoded teacher login
        if email == 'gaurav443201' and password == '443201':
            session['user_id'] = 1
            session['user_name'] = 'Gaurav (Teacher)'
            
            # Ensure the user exists in MySQL to prevent foreign key constraint errors
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("INSERT IGNORE INTO users (id, name, email, password) VALUES (1, 'Gaurav', 'gaurav443201', '443201')")
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                pass
                
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
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM subjects WHERE user_id = %s", (user_id,))
        subjects = cursor.fetchall()
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
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
        cursor.execute("INSERT INTO subjects (user_id, subject_name, total_classes, attended_classes) VALUES (%s, %s, %s, %s)",
                       (user_id, name, total, attended))
        conn.commit()
        flash("Subject added successfully!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
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
        cursor.execute("UPDATE subjects SET subject_name=%s, total_classes=%s, attended_classes=%s WHERE subject_id=%s AND user_id=%s",
                       (name, total, attended, subject_id, user_id))
        conn.commit()
        flash("Subject updated!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            
    return redirect(url_for('dashboard'))

@app.route('/subject/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    user_id = session['user_id']
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE subject_id=%s AND user_id=%s", (subject_id, user_id))
        conn.commit()
        flash("Subject deleted!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
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
            cursor.execute("UPDATE subjects SET total_classes=total_classes+1, attended_classes=attended_classes+1 WHERE subject_id=%s AND user_id=%s", (subject_id, user_id))
        elif action == 'bunk':
            cursor.execute("UPDATE subjects SET total_classes=total_classes+1 WHERE subject_id=%s AND user_id=%s", (subject_id, user_id))
        conn.commit()
    except Exception as e:
        flash(f"Database error: {e}", "danger")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            
    return redirect(url_for('dashboard'))
    
@app.route('/api/chart_data')
@login_required
def chart_data():
    user_id = session['user_id']
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT subject_name, total_classes, attended_classes FROM subjects WHERE user_id = %s", (user_id,))
        subjects = cursor.fetchall()
        
        labels = []
        attendance_rates = []
        for sub in subjects:
            labels.append(sub['subject_name'])
            perc = (sub['attended_classes'] / sub['total_classes'] * 100) if sub['total_classes'] > 0 else 0
            attendance_rates.append(round(perc, 2))
            
        return jsonify({'labels': labels, 'data': attendance_rates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
