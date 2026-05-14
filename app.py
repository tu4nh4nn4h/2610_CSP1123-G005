from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "your_secret_key"
s = URLSafeTimedSerializer("your-secret-key")

# Configuration Email
EMAIL_ADDRESS = 'zuhairanafey@gmail.com'
EMAIL_PASSWORD = 'zoqv itsk nuaf xuhm' 

def send_verification_email(to_email, token):
    verify_url = f"http://127.0.0.1:5000/verify_email/{token}"
    msg = MIMEText(f"Please click the link to verify your email:\n{verify_url}")
    msg['Subject'] = 'Email Verification'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    try: 
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        if 'server' in locals():
            server.quit()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_general (
                        student_email TEXT PRIMARY KEY,
                        student_id TEXT NOT NULL UNIQUE,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        keyword TEXT,
                        role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin')),
                        is_verified INTEGER DEFAULT 0
                     )''')
    # Event Registration Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS event_registrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        student_email TEXT NOT NULL,
                        personal_email TEXT,
                        phone_number TEXT NOT NULL,
                        faculty TEXT NOT NULL
                    )''')
    # Events Table (PENTING: Supaya create_event tidak error)
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_name TEXT NOT NULL,
                        description TEXT,
                        date TEXT,
                        time TEXT,
                        location TEXT
                    )''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users_general WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            if user['is_verified'] == 0:
                return "Please verify your email."
            session['user'] = username
            return redirect(url_for('eventbrowsing'))
        return "Invalid credentials"
    return render_template('signin.html')

@app.route('/eventbrowsing')
def eventbrowsing():
    return render_template('EventDisBrow.html')

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    events = {
        1: {"name": "Hackathon 2026", "date": "2026-06-01", "time": "09:00 AM", "venue": "Lab 1", "desc": "Build something real."},
        2: {"name": "Food Festival 2026", "date": "2026-05-25", "time": "10:00 AM", "venue": "Grand Hall", "desc": "Explore amazing food."},
        3: {"name": "MMU Fun Run 2026", "date": "2026-06-10", "time": "07:00 AM", "venue": "Stadium", "desc": "Get active!"},
        4: {"name": "MMU Career Talk 2026", "date": "2026-06-15", "time": "02:00 PM", "venue": "Theater", "desc": "Industry sharing."}
    }
    event = events.get(event_id)
    return render_template('eventregsys.html', event=event, event_id=event_id)

@app.route('/form')
def form():
    event_id = request.args.get('event_id', 1)
    return render_template('form.html', event_id=event_id)

@app.route('/register', methods=['POST'])
def register_event():
    data = request.get_json()
    

    print(f"Data diterima dari JS: {data}")

    conn = get_db_connection()
    try:
        
        conn.execute("""
            INSERT INTO event_registrations 
            (name, student_id, student_email, personal_email, phone_number, faculty)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get('name'), 
            data.get('studentId'), 
            data.get('studentEmail'), 
            data.get('personalEmail'), 
            data.get('phone'), 
            data.get('faculty')
        ))
        conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"RALAT DATABASE: {e}") # Tengok terminal VS Code untuk baca error ni
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
@app.route('/createevent', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
       
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO events (event_name, description, date, time, location) VALUES (?, ?, ?, ?, ?)",
                         (request.form['Event_name'], request.form['Event_description'], 
                          request.form['Event_date'], request.form['Event_time'], request.form['Event_location']))
            conn.commit()
            return redirect(url_for('eventbrowsing'))
        finally:
            conn.close()
    return render_template('create_event.html')

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)