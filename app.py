from fileinput import filename
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
import pandas as pd
from flask import send_file
import io
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"
s = URLSafeTimedSerializer("your-secret-key")
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

EVENT_POSTER_FOLDER = 'static/eventPoster'
ALLOWED_POSTER_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['EVENT_POSTER_FOLDER'] = EVENT_POSTER_FOLDER

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
            e.start_date AS date,
            e.start_time AS time
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

def allowed_poster_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_POSTER_EXTENSIONS

def create_notification(student_id, message, type):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notifications
        (student_id, message, type)
        VALUES (?, ?, ?)
    """, (student_id, message, type))

    conn.commit()
    conn.close()

def setup_database():
    conn = get_db_connection()
    with open('database_schema.sql', 'r', encoding='utf-8') as f:conn.executescript(f.read())

    conn.commit()
    conn.close()
    
@app.route('/')
def home():
    setup_database()
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
                    flash("Please verify your email before logging in.")
                    return redirect(url_for('signin'))
                
                session['user'] = username  # Assuming the first column is user ID
                return redirect(url_for('eventbrowsing'))
            else:
                flash("Invalid username or password")
        else:
            flash("Invalid username or password")
        
        
     
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
        cursor.execute(
            "SELECT student_id FROM users_general WHERE username = ?", (username,)
        )
        result = cursor.fetchone()
        student_id = result[0] if result else None
        conn.commit()
        conn.close()
        create_notification(
            student_id,
            "Your password has been changed successfully.",
            "Password Changed"
    )

        session.pop('reset_user', None)
        return redirect(url_for('signin'))

    return render_template('ResetPassword.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('Name')
        email = request.form.get('Email')
        username = request.form.get('Username')
        student_id = request.form.get('Student_id')
        club_body = request.form.get('Club_body')
        position_title = request.form.get('Position/title')
        password = request.form.get('Password')
        confirm_password = request.form.get('confirmPassword')
        keyword = request.form.get('keyword')
        security_question = request.form.get('security_question')

        if password != confirm_password:
            return "Passwords do not match"

        try:
            cursor.execute("INSERT INTO users_general (student_id, name, username, email, password, security_question, keyword, role, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (student_id, name, username, email, generate_password_hash(password), security_question, keyword, 'organizer', 0))
            cursor.execute("INSERT INTO organizer_details (student_id, club_body, position_title) VALUES (?, ?, ?)",
                            (student_id, club_body, position_title))
            conn.commit()

            token = s.dumps(email, salt='email-confirm')

            send_verification_email(email, token)  # Implement this function to send the email

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

    cursor.execute("SELECT password, student_id FROM users_general WHERE username = ?", (username,))
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
    create_notification(
        result["student_id"],
        "Your password has been changed successfully.",
        "Password Changed"
    )

    return "Password updated successfully"


@app.route('/eventbrowsing')
def eventbrowsing():
    # Fetch all events from the real SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT event_id, event_name, event_description, start_date, main_location FROM events")
    db_events = cursor.fetchall()
    conn.close()
    
    return render_template('EventDisBrow.html', events=db_events)
   
@app.route('/eventregister')
def eventregister():
    return render_template('eventregsys.html')


@app.route('/event/<int:event_id>')
def event_detail(event_id):
    # Fetch the specific event matching the ID from your database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    
    if not event:
        return "Event not found", 404

    # Renders your registration system page, passing the actual database item
    return render_template('eventregsys.html', event=event)


@app.route('/form', methods=['GET', 'POST'])
def form():
    event_id = request.args.get('event_id')
    if not event_id:
        return "Missing event tracking identifier", 400
        
    # Autofill logic: Get current logged-in user profile info
    username = session.get('user')
    user_data = None
    
    if username:
        conn = get_db_connection()
        # Row factory handles dictionary key lookups seamlessly
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Fetch only guaranteed columns to avoid phone/faculty column mismatch crashes
            cursor.execute("""
                SELECT student_id, name, email 
                FROM users_general WHERE username = ?
            """, (username,))
            user_data = cursor.fetchone()
        except sqlite3.OperationalError:
            # Fallback to empty form data if a database structure issue occurs
            user_data = None
        finally:
            conn.close()

    return render_template('form.html', event_id=event_id, user=user_data)


@app.route('/register_event', methods=['POST'])
def register_event():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400
        
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Get Event Name for personalized dashboard notification matching
        cursor.execute("SELECT event_name FROM events WHERE event_id = ?", (data.get('event_id'),))
        event_row = cursor.fetchone()
        event_name = event_row['event_name'] if event_row else "an event"

        # 1. Save registration (Matched directly to your 7 event_registrations schema columns)
        cursor.execute("""
            INSERT INTO event_registrations
            (event_id, name, student_id, email, phone_number, faculty)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get('event_id'),
            data.get('name'),
            data.get('studentId'),
            data.get('studentEmail'), # Maps frontend studentEmail to 'email' column
            data.get('phone'),        # Maps frontend phone to 'phone_number' column
            data.get('faculty')       # Captured from the manual frontend drop-down choice
        ))

        # 2. Dynamic Dashboard Notification creation
        cursor.execute("""
            INSERT INTO notifications (student_id, message, type)
            VALUES (?, ?, ?)
        """, (
            data.get('studentId'),
            f"You have successfully registered for the event: {event_name}.",
            "confirmation"
        ))

        response_data = {
            "status": "success",
            "message": "Registration successful"
        }

        # 3. Calendar Data Construction Package (.ics generation for Outlook)
        if data.get('outlook_calendar'):
            cursor.execute("""
                SELECT event_name, event_description, start_date, end_date, 
                       start_time, end_time, main_location, general_location, 
                       faculty_wing, specific_location 
                FROM events WHERE event_id = ?
            """, (data.get('event_id'),))
            event = cursor.fetchone()

            if event:
                if event['main_location'] == 'General':
                    location = event['general_location'] or "Online/General"
                else:
                    parts = [event['main_location'], event['faculty_wing'], event['specific_location']]
                    location = ", ".join([p for p in parts if p])

                # Clean date/time formats for standard vCalendar specifications
                clean_start_date = event['start_date'].replace("-", "")
                clean_end_date = event['end_date'].replace("-", "")
                clean_start_time = event['start_time'].replace(":", "")
                clean_end_time = event['end_time'].replace(":", "")

                if len(clean_start_time) == 4: clean_start_time += "00"
                if len(clean_end_time) == 4: clean_end_time += "00"

                dtstart = f"{clean_start_date}T{clean_start_time}"
                dtend = f"{clean_end_date}T{clean_end_time}"
                dtstamp = datetime.now().strftime('%Y%m%dT%H%M%S')

            ics_template = (
                    "BEGIN:VCALENDAR\n"
                        "VERSION:2.0\n"
                        "PRODID:-//UniSphere//Event Management//EN\n"
                        "BEGIN:VEVENT\n"
                        f"UID:event_{data.get('event_id')}_{data.get('studentId')}@unisphere.edu\n"
                        f"DTSTAMP:{dtstamp}\n"
                        # Added TZID parameter so Outlook knows this is strictly Malaysia Time
                        f"DTSTART;TZID=Asia/Kuala_Lumpur:{dtstart}\n"
                        f"DTEND;TZID=Asia/Kuala_Lumpur:{dtend}\n"
                        f"SUMMARY:{event['event_name']}\n"
                        f"DESCRIPTION:{event['event_description']}\n"
                        f"LOCATION:{location}\n"
                        "END:VEVENT\n"
                        "END:VCALENDAR"
                    )

            response_data["download_calendar"] = True
            response_data["ics_content"] = ics_template
            response_data["filename"] = f"event_{data.get('event_id')}.ics"

        conn.commit()
        return jsonify(response_data)

    except Exception as e:
        conn.rollback()
        print("Registration Error Details:", str(e)) # Server terminal diagnostic log
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()
        
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
        event_poster = None

        if 'eventPoster' in request.files:
            file = request.files['eventPoster']

            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename.strip())
                unique_filename = str(uuid.uuid4()) + "_" + filename
                file.save(os.path.join(app.config['EVENT_POSTER_FOLDER'], unique_filename))
                event_poster = unique_filename

        event_name = request.form.get('eventName')
        event_description = request.form.get('eventDescription')
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')
        start_time = request.form.get('startTime')
        end_time = request.form.get('endTime')
        event_mode = request.form.get('eventMode')

        main_location = request.form.get('mainLocation')

        if main_location == 'General':
            general_location = request.form.get('generalLocation')
            faculty_wing = None
            specific_location = None
        else:
            general_location = None
            faculty_wing = request.form.get('facultyWing')
            specific_location = request.form.get('specificLocation')

        participation_option = request.form.get('participationOption')
        if participation_option == "unlimited":
            limited_max_participants = None
        else:
            limited_max_participants = request.form.get('limitedMaxParticipants')

        event_link = request.form.get('eventLink')

        try:
            cursor.execute("""
                INSERT INTO events
                (event_poster, event_name, event_description, start_date, end_date, start_time, end_time, event_mode, main_location, general_location, faculty_wing, specific_location, participation_option, limited_max_participants, event_link, student_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_poster, event_name, event_description, start_date, end_date, start_time, end_time, event_mode, main_location, general_location, faculty_wing, specific_location, participation_option, limited_max_participants, event_link, user['student_id']))

            conn.commit()
            return jsonify({"status": "create_event_success"})
        
        except Exception as e:
            conn.rollback()
            return jsonify({
            "status": "create_event_failed",
            "message": str(e)
            })

        finally:
            conn.close()
            create_notification(
            user["student_id"],
                "Your event has been created successfully.",
                "Event Created"
            )

@app.route('/be_organizer', methods=['GET', 'POST'])
def be_organizer():
    username = session.get('user')
    conn = get_db_connection()
    cursor = conn.cursor()

    if not username:
        return redirect(url_for('signin'))

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

@app.route('/myevent')
def my_event():

    username = session.get('user')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT student_id, role FROM users_general WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if not user:
        conn.close()
        return redirect(url_for('signin'))

    # ONLY ORGANIZER CAN ACCESS
    if user['role'] != 'organizer':
        conn.close()
        return redirect(url_for('dashboard'))

    cursor.execute("""SELECT * FROM events WHERE student_id = ?""", (user['student_id'],))

    events = cursor.fetchall()
    conn.close()

    return render_template('my_event.html',user=user, events=events)

@app.route('/myevent/<int:event_id>')
def my_event_manage(event_id):
    # Fetch the specific event matching the ID from your database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event = cursor.fetchone()

    if not event:
        conn.close()
        return redirect(url_for('myevent'))
    
    cursor.execute("""SELECT * FROM event_registrations WHERE event_id = ?""", (event_id,))

    participants = cursor.fetchall()
    conn.close()

    return render_template('my_event_manage.html',event=event,participants=participants)

@app.route('/exportevent/<int:event_id>')
def export_event(event_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECTname,student_id,email,phone_number,faculty FROM event_registrations WHERE event_id = ?""", (event_id,))

    participants = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(participants,columns=['Name','Student ID','Email','Phone Number','Faculty'])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False, sheet_name='Participants Analysis')
    output.seek(0)

    return send_file(output,as_attachment=True,download_name=f'event_{event_id}_participants.xlsx',mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/deleteevent/<int:event_id>', methods=['POST'])
def delete_event(event_id):

    username = session.get('user')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT event_name FROM events WHERE event_id = ?""", (event_id,))
    event = cursor.fetchone()

    if not event:
        conn.close()
        return redirect(url_for('myevent'))

    # Get all participants
    cursor.execute("""SELECT student_id FROM event_registrations WHERE event_id = ?""", (event_id,))
    participants = cursor.fetchall()

    # # Send notification
    # for participant in participants:

    #     cursor.execute("""INSERT INTO notifications (student_id, message, type) VALUES (?, ?, ?)""",
    #     (participant['student_id'], f"The event '{event['event_name']}' has been cancelled by the organizer.",'event_cancelled'))

    # Delete registrations first
    cursor.execute("""DELETE FROM event_registrations WHERE event_id = ?""", (event_id,))

    # # Delete tag mapping
    # cursor.execute("""DELETE FROM event_tag_map WHERE event_id = ?""", (event_id,))

    # Delete event
    cursor.execute("""DELETE FROM events WHERE event_id = ?""", (event_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('myevent'))

@app.route('/user_dashboard1')
def dashboard():
    username = session.get('user')
    if not username:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch logged-in user profile information
    cursor.execute("""
        SELECT * FROM users_general 
        LEFT JOIN user_details ON users_general.student_id = user_details.student_id 
        WHERE users_general.username = ?
    """, (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found"

   # 2. Query only the events that THIS specific student has registered for using an INNER JOIN
    # Fixed: Matched exactly to the schema columns found in EventRegSys.html
    cursor.execute("""
        SELECT e.event_id, e.event_name, e.event_description, 
               e.start_date, e.end_date, e.start_time, e.end_time, 
               e.main_location, e.event_mode
        FROM events e
        INNER JOIN event_registrations er ON e.event_id = er.event_id
        WHERE er.student_id = ?
    """, (user["student_id"],))
    
    events = cursor.fetchall()
    conn.close()

    # 3. Pass both 'user' object and 'events' list to the HTML template layout dashboard
    return render_template('user_dashboard1.html', user=user, events=events)


@app.route("/cancel_registration/<int:event_id>", methods=["POST"])
def cancel_registration(event_id):
    username = session.get('user')
    if not username:
        return redirect(url_for('signin'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Fetch the unique student_id based on the active session username
        cursor.execute("SELECT student_id FROM users_general WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            return "User not found"

        student_id = user["student_id"]

        # 2. Fetch the event name before deleting to generate a personalized notification log entry
        cursor.execute("SELECT event_name FROM events WHERE event_id = ?", (event_id,))
        event_data = cursor.fetchone()
        event_name = event_data["event_name"] if event_data else "an Event"

        # 3. Securely delete ONLY this particular student's specific registration record
        cursor.execute("""
            DELETE FROM event_registrations
            WHERE event_id = ?
            AND student_id = ?
        """, (event_id, student_id))

        # 4. Insert a new cancellation entry with the required 'type' field included
        notification_msg = f"You have successfully cancelled your registration for '{event_name}'."
        
        # Added 'type' column to satisfy the database NOT NULL constraint
        cursor.execute("""
            INSERT INTO notifications (student_id, message, type)
            VALUES (?, ?, ?)
        """, (student_id, notification_msg, 'Cancellation'))

        # Commit all changes to the database safely
        conn.commit()
        flash("Registration cancelled successfully.")

    except sqlite3.OperationalError as e:
        print(f"Database Error encountered: {e}")
        conn.rollback() 
        return "The database is currently busy. Please try again in a few seconds."
        
    finally:
        conn.close()

    # Clean redirect back to the main user profile dashboard page view
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
        create_notification(
            user["student_id"],
            "Your profile information has been updated successfully.",
            "Profile Updated"
        )

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
    
    if not user:
        conn.close()
        return "User not found"

    # Preserving your original structure system function logic framework layer
    create_event_reminders(user["student_id"])

    # 5. Fetch all user notifications sorted chronologically, including the fresh cancellation text row log entry
    cursor.execute("""
        SELECT * FROM notifications
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (user["student_id"],))

    notifications_list = cursor.fetchall()
    conn.close()

    return render_template("notifications.html", notifications=notifications_list)

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
        "SELECT email, student_id FROM users_general WHERE username = ?",
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
    create_notification(
        user["student_id"],
        "Your email address has been changed successfully.",
        "Email Changed"
    )

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
    
@app.route('/mark_notification_read/<int:notification_id>')
def mark_notification_read(notification_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notifications
        SET is_read = 1
        WHERE id = ?
    """, (notification_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('notifications'))

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)