import os
import math
import threading
import time
import urllib.request
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')

# Background thread to keep Render server awake
def keep_awake():
    app_url = os.environ.get('RENDER_EXTERNAL_URL')
    if app_url:
        while True:
            try:
                time.sleep(600)  # Ping every 10 minutes
                urllib.request.urlopen(app_url)
            except Exception:
                pass

threading.Thread(target=keep_awake, daemon=True).start()

# MongoDB Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.get_database('bunk_manager')
subjects_collection = db.subjects

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
    
    try:
        # Fetch all subjects for this user
        subjects_cursor = subjects_collection.find({'user_id': user_id})
        subjects = list(subjects_cursor)
        
        # Convert ObjectId to string so it can be used in HTML
        for sub in subjects:
            sub['subject_id'] = str(sub['_id'])
    except Exception as e:
        flash(f"Database error: {e}", "danger")
        subjects = []
            
    # Process attendance logic
    overall_total = 0
    overall_attended = 0
    
    for sub in subjects:
        total = sub.get('total_classes', 0)
        attended = sub.get('attended_classes', 0)
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
        subject_doc = {
            'user_id': user_id,
            'subject_name': name,
            'total_classes': total,
            'attended_classes': attended
        }
        subjects_collection.insert_one(subject_doc)
        flash("Subject added successfully!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
            
    return redirect(url_for('dashboard'))

@app.route('/subject/edit/<subject_id>', methods=['POST'])
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
        subjects_collection.update_one(
            {'_id': ObjectId(subject_id), 'user_id': user_id},
            {'$set': {
                'subject_name': name,
                'total_classes': total,
                'attended_classes': attended
            }}
        )
        flash("Subject updated!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
            
    return redirect(url_for('dashboard'))

@app.route('/subject/delete/<subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    user_id = session['user_id']
    
    try:
        subjects_collection.delete_one({'_id': ObjectId(subject_id), 'user_id': user_id})
        flash("Subject deleted!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")
            
    return redirect(url_for('dashboard'))

@app.route('/subject/quick_add/<subject_id>/<action>', methods=['POST'])
@login_required
def quick_action(subject_id, action):
    user_id = session['user_id']
    
    try:
        if action == 'attend':
            subjects_collection.update_one(
                {'_id': ObjectId(subject_id), 'user_id': user_id},
                {'$inc': {'total_classes': 1, 'attended_classes': 1}}
            )
        elif action == 'bunk':
            subjects_collection.update_one(
                {'_id': ObjectId(subject_id), 'user_id': user_id},
                {'$inc': {'total_classes': 1}}
            )
    except Exception as e:
        flash(f"Database error: {e}", "danger")
            
    return redirect(url_for('dashboard'))
    
@app.route('/api/chart_data')
@login_required
def chart_data():
    user_id = session['user_id']
    try:
        subjects = list(subjects_collection.find({'user_id': user_id}))
        
        labels = []
        attendance_rates = []
        for sub in subjects:
            labels.append(sub.get('subject_name', 'Unknown'))
            total = sub.get('total_classes', 0)
            attended = sub.get('attended_classes', 0)
            perc = (attended / total * 100) if total > 0 else 0
            attendance_rates.append(round(perc, 2))
            
        return jsonify({'labels': labels, 'data': attendance_rates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
