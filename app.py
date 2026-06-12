from flask import Flask, flash, render_template, redirect, url_for, request, session, jsonify
from datetime import datetime, timedelta
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
import os
import uuid
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key"
s = URLSafeTimedSerializer("your-secret-key")
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
def send_verification_email(to_email, token):
    verify_url = f"http://127.0.0.1:5000/verify_email/{token}"

    msg = MIMEText(f"Please click the link to verify your email:\n{verify_url}")
    msg['Subject'] = 'Email Verification'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    try: 

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Use your email provider's SMTP server and port
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        if server:
            server.quit()

def send_email_change_verification(to_email, token):
    verify_url = f"http://127.0.0.1:5000/verify_new_email/{token}"

    msg = MIMEText(
        f"Click the link below to verify your new email:\n\n{verify_url}"
    )

    msg['Subject'] = 'Verify New Email Address'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

    except Exception as e:
        print(f"Error sending email: {e}")

    finally:
        server.quit()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

# =========================================
# EVENT REMINDER NOTIFICATION FUNCTION
# =========================================

def create_event_reminders(student_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    # =========================================
    # Get all events registered by the student
    # =========================================
    cursor.execute("""
        SELECT 
            e.event_id,
            e.event_name,
            e.date,
            e.time
        FROM event_registrations r
        JOIN events e
            ON r.event_id = e.event_id
        WHERE r.student_id = ?
    """, (student_id,))

    events = cursor.fetchall()

    # =========================================
    # Get today's date and tomorrow's date
    # =========================================
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    # =========================================
    # Loop through every registered event
    # =========================================
    for event in events:

        # Convert event date string into actual date format
        # IMPORTANT:
        # Change the format if your DB date format is different
        event_date = datetime.strptime(
            event["date"],
            "%Y-%m-%d"
        ).date()

        # =========================================
        # Check if event is tomorrow
        # =========================================
        if event_date == tomorrow:

            reminder_message = (
                f"Reminder: {event['event_name']} starts tomorrow at {event['time']}."
            )

            # =========================================
            # Prevent duplicate reminder notifications
            # =========================================
            cursor.execute("""
                SELECT *
                FROM notifications
                WHERE student_id = ?
                AND message = ?
            """, (student_id, reminder_message))

            existing_notification = cursor.fetchone()

            # =========================================
            # If reminder does not exist yet
            # Create notification
            # =========================================
            if not existing_notification:

                cursor.execute("""
                    INSERT INTO notifications
                    (student_id, message, type)
                    VALUES (?, ?, ?)
                """, (
                    student_id,
                    reminder_message,
                    "reminder"
                ))

    conn.commit()
    conn.close()
    
# checks all registered events
# compares event date with tomorrow
# if event is tomorrow:
  # creates reminder noti
# prevents duplicate reminder 

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # =========================
    # USERS TABLE
    # =========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_general (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            keyword TEXT,
            role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin')),
            is_verified INTEGER DEFAULT 0,
            pending_email TEXT,
            security_question TEXT
        )
    ''')

    # =========================
    # USER PROFILE DETAILS
    # =========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_details (
            student_id TEXT PRIMARY KEY,
            bio TEXT,
            birthday DATE,
            faculty TEXT,
            year_of_study INTEGER,
            profile_picture TEXT,
            FOREIGN KEY (student_id) REFERENCES users_general(student_id)
        )
    ''')

    # =========================
    # ORGANIZER DETAILS
    # =========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizer_details (
            student_id TEXT PRIMARY KEY,
            club_body TEXT NOT NULL,
            position_title TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES users_general(student_id)
        )
    ''')

    # =========================
    # EVENTS TABLE
    # =========================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        event_description TEXT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        event_mode TEXT NOT NULL CHECK(event_mode IN ('online', 'offline', 'hybrid')),
        main_location TEXT NOT NULL,         -- corresponds to id="mainloc"
        general_location TEXT,               -- optional, only for general locations
        faculty_wing TEXT,                   -- optional, only for faculty path
        specific_location TEXT,              -- optional, only for faculty path
        participants INTEGER NOT NULL,
        event_link TEXT,
        student_id varchar(10) NOT NULL,
        FOREIGN KEY (student_id) REFERENCES organizer_details(student_id)
        )
    ''')
    # =========================
    # EVENT TAGS
    # =========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_tag_map (
            event_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY(event_id, tag_id),
            FOREIGN KEY (event_id) REFERENCES events(event_id),
            FOREIGN KEY (tag_id) REFERENCES event_tags(tag_id)
        )
    ''')

    # =========================
    # EVENT REGISTRATIONS
    # =========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            student_id TEXT NOT NULL,
            student_email TEXT NOT NULL,
            personal_email TEXT,
            phone_number TEXT NOT NULL,
            faculty TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(event_id),
            FOREIGN KEY (student_id) REFERENCES users_general(student_id)
        )
    ''')

    # =========================
    # NOTIFICATIONS TABLE 
    # =========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users_general(student_id)
        )
    ''')

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
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users_general WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            stored_password = user[4]  # Assuming password is the 5th column
            is_verified = user[7]  # Assuming is_verified is the 8th column
              
            if check_password_hash(stored_password, password):
                if is_verified == 0:
                    return "Please verify your email before logging in."
                
                session['user'] = username  # Assuming the first column is user ID
                return redirect(url_for('eventbrowsing'))
            else:
                return "Invalid username or password"
        else:
            return "Invalid username or password"
        
        
     
    return render_template('signin.html')


@app.route('/verify_keyword', methods=['POST'])
def verify_keyword():
    username = request.form['username']
    keyword = request.form['keyword']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_general WHERE username = ? AND keyword = ?", (username, keyword))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['reset_user'] = username
        return redirect(url_for('reset_password'))

    return "Invalid username or keyword"


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_user' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        new_password = request.form['NewPassword']
        confirm_password = request.form['ConfirmNewPassword']

        if new_password != confirm_password:
            return "Passwords do not match"

        username = session['reset_user']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users_general SET password = ? WHERE username = ?",
            (generate_password_hash(new_password), username)
        )
        conn.commit()
        conn.close()

        session.pop('reset_user', None)
        return redirect(url_for('signin'))

    return render_template('ResetPassword.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('Name')
        email = request.form.get('Email')
        username = request.form.get('Username')
        student_id = request.form.get('Student_id')
        password = request.form.get('Password')
        confirm_password = request.form.get('confirmPassword')
        keyword = request.form.get('keyword')
        security_question = request.form.get('security_question')

        if password != confirm_password:
            return "Passwords do not match"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users_general (student_id, name, username, email, password, security_question, keyword, role, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (student_id, name, username, email, generate_password_hash(password), security_question, keyword, 'user', 0))
            conn.commit()

            token = s.dumps(email, salt='email-confirm')

            send_verification_email(email, token)  # Implement this function to send the email

        except sqlite3.IntegrityError:
            return "Username or email already exists"

        finally:
            conn.close()

        return redirect(url_for('signin'))

    return render_template('register.html')

@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)  # Token expires in 1 hour
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users_general SET is_verified = 1 WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return "Email verified successfully! You can now log in."
    except:
        return "The verification link is invalid or has expired."

@app.route('/register_organizer', methods=['GET', 'POST'])
def register_organizer():
    if request.method == 'POST':
        name = request.form['Name']
        email = request.form['Email']
        username = request.form['Username']
        student_id = request.form['Student_id']
        password = request.form['Password']
        confirm_password = request.form['confirmPassword']
        club_body = request.form['Club_body']
        position_title = request.form['Position_title']
        keyword = request.form.get('keyword')

        if password != confirm_password:
            return "Passwords do not match"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users_general
                (student_id, name, username, email, password, keyword, role)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, name, username, email,
                  generate_password_hash(password), keyword, 'organizer'))

            cursor.execute("""
                INSERT INTO organizer_details
                (student_id, club_body, position_title)
                VALUES (?, ?, ?)
            """, (student_id, club_body, position_title))

            conn.commit()

        except sqlite3.IntegrityError:
            return "Username or email already exists"

        finally:
            conn.close()

        return redirect(url_for('signin'))

    return render_template('register_organizer.html')


@app.route('/change_password', methods=['POST'])
def change_password():
    current = request.form['current_password']
    new = request.form['new_password']
    confirm = request.form['confirm_password']

    username = session.get('user')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users_general WHERE username = ?", (username,))
    result = cursor.fetchone()

    if not result:
        return "User not found"

    if not check_password_hash(result["password"], current):
        return "Current password is incorrect"

    if new != confirm:
        return "Passwords do not match"

    cursor.execute(
        "UPDATE users_general SET password = ? WHERE username = ?",
        (generate_password_hash(new), username)
    )

    conn.commit()
    conn.close()

    return "Password updated successfully"


@app.route('/eventbrowsing')
def eventbrowsing():
    return render_template('EventDisBrow.html')


@app.route('/eventregister')
def eventregister():
    return render_template('eventregsys.html')


@app.route('/event/<int:event_id>')
def event_detail(event_id):
    events = {
        1: {
            "name": "Hackathon 2026",
            "desc": "Build innovative solutions in a competitive environment.",
            "date": "20 May 2026",
            "time": "10:00 AM - 6:00 PM",
            "venue": "Dewan Tun Canselor, MMU Cyberjaya"
        },
        2: {
            "name": "Food Festival 2026",
            "desc": "Explore global cuisines and enjoy fun activities.",
            "date": "25 May 2026",
            "time": "10:00 AM - 10:00 PM",
            "venue": "Central Plaza, MMU Cyberjaya"
        },
        3: {
            "name": "MMU Fun Run 2026",
            "desc": "A fun and energetic community running event.",
            "date": "30 May 2026",
            "time": "8:00 AM - 5:00 PM",
            "venue": "Stadium MMU Cyberjaya"
        },
        4: {
            "name": "MMU Career Talk 2026",
            "desc": "Gain insights from industry professionals.",
            "date": "27 June 2026",
            "time": "10:00 AM - 4:00 PM",
            "venue": "CLC, MMU Cyberjaya"
        }
    }

    event = events.get(event_id)
    if not event:
        return "Event not found", 404

    return render_template('eventregsys.html', event=event)

@app.route('/form', methods=['GET', 'POST'])
def form():
    event_id = request.args.get('event_id', 1)
    return render_template('form.html', event_id=event_id)

@app.route('/register_event', methods=['POST'])
def register_event():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data received"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Save registration
    cursor.execute("""
        INSERT INTO event_registrations
        (name, student_id, student_email, personal_email, phone_number, faculty, event_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('name'),
        data.get('studentId'),
        data.get('studentEmail'),
        data.get('personalEmail'),
        data.get('phone'),
        data.get('faculty'),
        data.get('event_id')
))
    # 2. Create notification (IMPORTANT PART)
    cursor.execute("""
        INSERT INTO notifications (student_id, message, type)
        VALUES (?, ?, ?)
    """, (
        data.get('studentId'),
        "You have successfully registered for an event.",
        "confirmation"
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Registration successful"
    }) # now every registration will store notification & create notification automatically 

@app.route('/createevent', methods=['GET', 'POST'])
def create_event():

    username = session.get('user')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT student_id, role FROM users_general WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return redirect(url_for('signin'))

    if user["role"] != "organizer":
        conn.close()
        flash("Only organizers can create events. Please register as an organizer to create events.")
        return redirect(url_for('be_organizer'))
    
    if request.method == 'GET':
        return render_template('create_event.html')

    if request.method == 'POST':
        data=request.get_json()
        event_name = data.get('eventName')
        event_description = data.get('eventDescription')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        event_mode = data.get('eventMode')

        main_location = data.get('mainLocation')

        if main_location == 'General':
            general_location = data.get('generalLocation')
            faculty_wing = None
            specific_location = None
        else:
            general_location = None
            faculty_wing = data.get('facultyWing')
            specific_location = data.get('specificLocation')

        participant_limit = data.get('participants')
        event_link = data.get('eventLink')

        try:
            cursor.execute("""
                INSERT INTO events
                (event_name, event_description, start_date, end_date, start_time, end_time, event_mode, main_location, general_location, faculty_wing, specific_location, participant_limit, event_link, student_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_name, event_description, start_date, end_date, start_time, end_time, event_mode, main_location, general_location, faculty_wing, specific_location, participant_limit, event_link, user['student_id']))

            conn.commit()

        except Exception as e:
            conn.rollback()
            return f"Error: {e}"

        finally:
            conn.close()

        return jsonify({"status": "create_event_success"})


@app.route('/be_organizer', methods=['GET', 'POST'])
def be_organizer():

    username = session.get('user')

    if not username:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current user
    cursor.execute(""" SELECT student_id, role FROM users_general WHERE username = ?""", (username,))
    
    user = cursor.fetchone()

    if not user:
        conn.close()
        return redirect(url_for('signin'))

    # Already organizer
    if user['role'] == 'organizer':
        conn.close()
        return redirect(url_for('create_event'))

    if request.method == 'GET':
        return render_template('be_organizer.html')

    if request.method == 'POST':
        data=request.get_json()
        club_body = data.get('club_body')
        position_title = data.get('position_title')

        try:
            # Insert organizer details
            cursor.execute(""" INSERT INTO organizer_details (student_id, club_body, position_title) VALUES (?, ?, ?)""", 
                (user['student_id'], club_body,position_title))

            # Update role
            cursor.execute("""UPDATE users_general SET role = 'organizer' WHERE student_id = ?""", (user['student_id'],))

            conn.commit()

        except Exception as e:
            conn.rollback()
            return f"Error: {e}"

        finally:
            conn.close()

        return jsonify({"status": "become_organizer_success"})

@app.route('/user_dashboard1')
def dashboard():
    username = session.get('user')
    if not username:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_general LEFT JOIN user_details ON users_general.student_id = user_details.student_id WHERE users_general.username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return "User not found"

    return render_template('user_dashboard1.html', user=user)

@app.route('/cancel_event/<int:event_id>')
def cancel_event(event_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    # delete registration
    cursor.execute(
        "DELETE FROM event_registrations WHERE event_id = ?",
        (event_id,)
    )

    conn.commit()
    conn.close()

    flash("Registration cancelled successfully.")

    # redirect back to dashboard
    return redirect(url_for('dashboard'))

@app.route("/cancel_registration/<int:event_id>", methods=["POST"])
def cancel_registration(event_id):
    username = session.get('user')

    if not username:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # get student_id
    cursor.execute("SELECT student_id FROM users_general WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        return "User not found"

    student_id = user["student_id"]

    cursor.execute("""
        DELETE FROM event_registrations
        WHERE event_id = ?
        AND student_id = ?
    """, (event_id, student_id))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():

    username = session.get('user')

    if not username:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # GET user data
    cursor.execute("SELECT * FROM users_general WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found"
    
    student_id = user["student_id"]
    cursor.execute("SELECT * FROM user_details WHERE student_id = ?", (student_id,))
    details = cursor.fetchone()

    # UPDATE profile
    if request.method == 'POST':
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename.strip())
                unique_filename = str(uuid.uuid4()) + "_" + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                profile_picture = unique_filename

        bio = request.form['bio']
        birthday = request.form['birthday']
        faculty = request.form['faculty']
        year_of_study = request.form['year_of_study']

        if details:
            cursor.execute("""
                UPDATE user_details
                SET bio = ?, birthday = ?, faculty = ?, year_of_study = ?, profile_picture = ?
                WHERE student_id = ?
            """, (bio, birthday, faculty, year_of_study, profile_picture, student_id))

        else:
            cursor.execute("""
                INSERT INTO user_details (student_id, bio, birthday, faculty, year_of_study, profile_picture)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, bio, birthday, faculty, year_of_study, profile_picture))

        conn.commit()
        conn.close()
        
        return redirect(url_for('user_profile'))

    conn.close()
    return render_template('EditProfile.html', user=user, details=details)

@app.route('/UserProfile')
def user_profile():
    username = session.get('user')

    if not username:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users_general LEFT JOIN user_details ON users_general.student_id = user_details.student_id WHERE users_general.username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return "User not found"

    return render_template('UserProfile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))
 
# notification page
@app.route('/notifications')
def notifications():
    username = session.get('user')
    if not username:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id FROM users_general WHERE username = ?
    """, (username,))
    user = cursor.fetchone()
    
    # =========================================
    # CREATE EVENT REMINDERS
    # =========================================
    create_event_reminders(user["student_id"])

    if not user:
        conn.close()
        return "User not found"

    cursor.execute("""
        SELECT * FROM notifications
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (user["student_id"],))

    notifications = cursor.fetchall()
    conn.close()

    return render_template("notifications.html", notifications=notifications)

@app.route('/change_email', methods=['POST'])
def change_email():
    if 'user' not in session:
        return redirect(url_for('signin'))

    current_email = request.form['current_email']
    new_email = request.form['new_email']
    username = session['user']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email FROM users_general WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found"

    if user[0] != current_email:
        conn.close()
        return "Current email is incorrect"

    # Store new email temporarily
    cursor.execute("""
        UPDATE users_general
        SET pending_email = ?, is_verified = 0
        WHERE username = ?
    """, (new_email, username))

    conn.commit()
    conn.close()

    token = s.dumps(
        {'username': username, 'new_email': new_email},
        salt='change-email'
    )

    send_email_change_verification(new_email, token)

    return "Verification email sent to your new email address."

@app.route('/verify_new_email/<token>')
def verify_new_email(token):
    try:
        data = s.loads(
            token,
            salt='change-email',
            max_age=3600
        )

        username = data['username']
        new_email = data['new_email']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users_general
            SET email = ?,
                pending_email = NULL,
                is_verified = 1
            WHERE username = ?
        """, (new_email, username))

        conn.commit()
        conn.close()

        return "New email verified successfully. You can now log in."

    except Exception:
        return "Verification link is invalid or expired."

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)