import os
import math
import threading
import time
import urllib.request
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
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
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
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
        
        # Hardcoded student login
        if email == 'gaurav443201' and password == '443201':
            session['user_id'] = 1
            session['user_name'] = 'Gaurav'
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
        
        # Convert ObjectId to string so it can be used in HTML and JSON serialization
        for sub in subjects:
            sub['subject_id'] = str(sub['_id'])
            del sub['_id']  # Remove raw ObjectId to prevent JSON serialization crashes
    except Exception as e:
        flash(f"Database error: {e}", "danger")
        subjects = []
            
    # Process attendance logic
    overall_total = 0
    overall_attended = 0
    
    for sub in subjects:
        total = sub.get('total_classes', 0)
        attended = sub.get('attended_classes', 0)
        exclude = sub.get('exclude_attendance', False)
        
        if not exclude:
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
    
    user_doc = db.users.find_one({'_id': user_id}) or {}
    timetable_context = user_doc.get('timetable_context')
    sem_start = user_doc.get('sem_start', '')
    sem_end = user_doc.get('sem_end', '')
    
    return render_template('dashboard.html', subjects=subjects, overall_percent=overall_percent, timetable_context=timetable_context, sem_start=sem_start, sem_end=sem_end)

@app.route('/subject/add', methods=['POST'])
@login_required
def add_subject():
    name = request.form.get('subject_name')
    subject_type = request.form.get('subject_type', 'Theory')
    batch = request.form.get('batch', '')
    exclude_attendance = True if request.form.get('exclude_attendance') == 'on' else False
    
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
            'subject_type': subject_type,
            'batch': batch,
            'exclude_attendance': exclude_attendance,
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
    subject_type = request.form.get('subject_type', 'Theory')
    batch = request.form.get('batch', '')
    exclude_attendance = True if request.form.get('exclude_attendance') == 'on' else False
    
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
                'subject_type': subject_type,
                'batch': batch,
                'exclude_attendance': exclude_attendance,
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
        subjects = list(subjects_collection.find({'user_id': user_id, 'exclude_attendance': {'$ne': True}}))
        
        labels = []
        attendance_rates = []
        for sub in subjects:
            tag = f" ({sub.get('batch')})" if sub.get('subject_type') == 'Practical' else ""
            labels.append(sub.get('subject_name', 'Unknown') + tag)
            total = sub.get('total_classes', 0)
            attended = sub.get('attended_classes', 0)
            perc = (attended / total * 100) if total > 0 else 0
            attendance_rates.append(round(perc, 2))
            
        return jsonify({'labels': labels, 'data': attendance_rates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import openai

@app.route('/api/chatgpt_suggestion')
@login_required
def chatgpt_suggestion():
    user_id = session['user_id']
    try:
        subjects = list(subjects_collection.find({'user_id': user_id}))
        
        if not subjects:
            return jsonify({'suggestion': "You don't have any subjects right now! Add some classes and I'll give you a personalized strategy."})
            
        prompt = "I am a college student requesting advice from a friendly, chill buddy. Here is my current attendance:\n"
        overall_total = 0
        overall_attended = 0
        for sub in subjects:
            t = sub.get('total_classes', 0)
            a = sub.get('attended_classes', 0)
            exclude = sub.get('exclude_attendance', False)
            if not exclude:
                overall_total += t
                overall_attended += a
            perc = round((a/t*100), 2) if t > 0 else 0
            tag = f" ({sub.get('batch')})" if sub.get('subject_type') == 'Practical' else " (Lecture)"
            prompt += f"- {sub.get('subject_name')}{tag}: {perc}% ({a}/{t})\n"
            
        overall_perc = round((overall_attended/overall_total*100), 2) if overall_total > 0 else 0
        prompt += f"\nMy overall attendance is {overall_perc}%. The minimum required is 75%.\n"
        
        # Add Timetable Context
        user_doc = db.users.find_one({'_id': user_id})
        if user_doc:
            if user_doc.get('timetable_context'):
                prompt += f"\nHere is my weekly timetable schedule: {user_doc.get('timetable_context')}\n"
            if user_doc.get('sem_start') and user_doc.get('sem_end'):
                prompt += f"My semester started on {user_doc.get('sem_start')} and ends on {user_doc.get('sem_end')}. Use these dates to roughly estimate how much of the semester is left and whether my current attendance allows me to relax or if I need to grind."
            
        if user_doc and user_doc.get('timetable_context'):
            prompt += "\nPlease give me short, chill, bro-like advice in 2-3 sentences. Tell me specifically using my timetable what days/classes I can bunk, or if I'm in danger. Be supportive!"
        else:
            prompt += "\nGive me a short, friendly, bro-like advice in exactly 2-3 sentences. Tell me what I should focus on, if I can relax, or if I'm in danger. Be supportive!"

        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({'suggestion': "Hey bro! Set up your OPENAI_API_KEY in the environment variables, and I'll give you a custom attendance strategy using AI! For now, just try to keep everything above 75%!"})
            
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly, chill college buddy helping your friend manage their class attendance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return jsonify({'suggestion': response.choices[0].message.content.strip()})
        
    except Exception as e:
        return jsonify({'suggestion': f"Oops, couldn't access my brain right now! Make sure your OpenAI API key is correct. ({str(e)})"})

import base64
import fitz  # PyMuPDF

@app.route('/api/upload_timetable', methods=['POST'])
@login_required
def upload_timetable():
    user_id = session['user_id']
    if 'timetable' not in request.files:
        return jsonify({'error': 'No file found'}), 400
        
    file = request.files['timetable']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        return jsonify({'error': 'OPENAI_API_KEY is missing. AI cannot read files.'}), 400
        
    try:
        import openai
        client = openai.OpenAI(api_key=openai_api_key)
        
        file_bytes = file.read()
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            # Instantly convert the PDF into a clear image array using PyMuPDF
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            page = pdf_document.load_page(0)  # Grab the first page
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # High resolution
            base64_image = base64.b64encode(pix.tobytes("jpeg")).decode('utf-8')
        else:
            base64_image = base64.b64encode(file_bytes).decode('utf-8')
        
        import json
        
        division = request.form.get('division', '')
        branch = request.form.get('branch', '')
        
        sys_prompt = "You are a timetable parser. Extract all unique subjects from the timetable image. Distinguish between Lectures and Practicals based on the schedule. If a practical has a batch, extract it. Return a JSON object exactly like this:\n{\n  \"subjects\": [\n    {\"subject_name\": \"string\", \"subject_type\": \"Lecture\"|\"Practical\", \"batch\": \"string or empty\", \"exclude_attendance\": boolean}\n  ],\n  \"summary\": \"A short 2-sentence summary of when the student's busiest days are from the schedule.\"\n}\n"
        sys_prompt += "CRITICAL RULE: Expand short abbreviated subject names into their FULL FORMS if they match these known subjects: DM -> 'Discrete Mathematics', COM or MP -> 'Computer Org and Microprocessor', OE -> 'Open Elective', IOT -> 'Internet of Things', MIL -> 'Modern Indian Languages', WD or Web Dev -> 'Web Development', MP Lab -> 'Microprocessor Lab', EPD -> 'Engineering Product Design', EVS -> 'Environmental Studies'. "
        
        if division or branch:
            sys_prompt += f"EXTREMELY IMPORTANT: The user's specific Division is '{division}' and Branch/Batch is '{branch}'. You MUST filter out all other branches/divisions and ONLY extract classes that this specific student would attend! Ignore all other columns."
        
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": sys_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the subjects and summary from this timetable image to JSON format."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            max_tokens=500
        )
        
        data_json = json.loads(response.choices[0].message.content.strip())
        
        # Insert subjects to MongoDB
        extracted_subjects = data_json.get('subjects', [])
        added_count = 0
        for sub in extracted_subjects:
            s_name = sub.get('subject_name')
            if not s_name: continue
            s_type = sub.get('subject_type', 'Lecture')
            s_batch = sub.get('batch', '')
            exclude = sub.get('exclude_attendance', False)
            
            # Upsert ensures we don't overwrite attended_classes if it already exists!
            res = subjects_collection.update_one(
                {
                    'user_id': user_id, 
                    'subject_name': s_name, 
                    'subject_type': s_type,
                    'batch': s_batch
                },
                {
                    '$setOnInsert': {
                        'exclude_attendance': exclude,
                        'total_classes': 0,
                        'attended_classes': 0
                    }
                },
                upsert=True
            )
            if res.upserted_id:
                added_count += 1
        
        parsed_schedule = data_json.get('summary', 'Timetable synced.')
        
        # Save summary string to Context for ChatGPT Prediction
        db.users.update_one(
            {'_id': user_id},
            {'$set': {'timetable_context': parsed_schedule}},
            upsert=True
        )
        
        return jsonify({'success': True, 'message': f'Timetable AI added {added_count} new subjects automatically!', 'data': parsed_schedule})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_semester_dates', methods=['POST'])
@login_required
def save_semester_dates():
    user_id = session['user_id']
    start_date = request.form.get('sem_start')
    end_date = request.form.get('sem_end')
    
    try:
        db.users.update_one(
            {'_id': user_id},
            {'$set': {'sem_start': start_date, 'sem_end': end_date}},
            upsert=True
        )
        flash("Semester dates saved successfully! AI will now factor this into your predictions.", "success")
    except Exception as e:
        flash(f"Error saving dates: {e}", "danger")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
