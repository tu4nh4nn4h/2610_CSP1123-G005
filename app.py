from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
app.secret_key = "your_secret_key"
s = URLSafeTimedSerializer("your-secret-key")

EMAIL_ADDRESS = 'zuhairanafey@gmail.com'
EMAIL_PASSWORD = 'zoqv itsk nuaf xuhm'  # Use an app-specific password for Gmail
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


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    return conn


def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users_general (
                        student_id varchar(10) PRIMARY KEY,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        keyword TEXT,
                        role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin'))
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_details (
                        student_id TEXT PRIMARY KEY,
                        bio TEXT,
                        birthday DATE,
                        faculty TEXT,
                        year_of_study INTEGER,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS organizer_details (
                        student_id TEXT PRIMARY KEY,
                        club_body TEXT NOT NULL,
                        position_title TEXT NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        location TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES organizer_details(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS event_tags (
                        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tag_name TEXT UNIQUE NOT NULL
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS event_tag_map (
                        event_id INTEGER NOT NULL,
                        tag_id INTEGER NOT NULL,
                        PRIMARY KEY(event_id, tag_id),
                        FOREIGN KEY (event_id) REFERENCES events(event_id),
                        FOREIGN KEY (tag_id) REFERENCES event_tags(tag_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_details (
                        student_id varchar(10) PRIMARY KEY,
                        bio TEXT,
                        birthday DATE,
                        faculty TEXT,
                        year_of_study INTEGER,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS organizer_details (
                        student_id varchar(10) PRIMARY KEY,
                        club_body TEXT NOT NULL,
                        position_title TEXT NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        location TEXT NOT NULL,
                        student_id varchar(10) NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES organizer_details(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS event_tags (
                        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tag_name TEXT UNIQUE NOT NULL
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS event_tag_map (
                        event_id INTEGER NOT NULL,
                        tag_id INTEGER NOT NULL,
                        PRIMARY KEY(event_id, tag_id),
                        FOREIGN KEY (event_id) REFERENCES events(event_id),
                        FOREIGN KEY (tag_id) REFERENCES event_tags(tag_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_details (
                        student_id varchar(10) PRIMARY KEY,
                        bio TEXT,
                        birthday DATE,
                        faculty TEXT,
                        year_of_study INTEGER,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS organizer_details (
                        student_id varchar(10) PRIMARY KEY,
                        club_body TEXT NOT NULL,
                        position_title TEXT NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        location TEXT NOT NULL,
                        student_id varchar(10) NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES organizer_details(student_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS event_tags (
                        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tag_name TEXT UNIQUE NOT NULL
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS event_tag_map (
                        event_id INTEGER NOT NULL,
                        tag_id INTEGER NOT NULL,
                        PRIMARY KEY(event_id, tag_id),
                        FOREIGN KEY (event_id) REFERENCES events(event_id),
                        FOREIGN KEY (tag_id) REFERENCES event_tags(tag_id)
                     )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS event_registrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        student_id varchar(10) NOT NULL,
                        student_email TEXT NOT NULL,
                        personal_email TEXT,
                        phone_number TEXT NOT NULL,
                        faculty TEXT NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id),
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
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
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users_general WHERE username = ?", (username,))
        user = cursor.fetchone()
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
        name = request.form['Name']
        email = request.form['Email']
        username = request.form['Username']
        student_id = request.form['Student_id']
        password = request.form['Password']
        confirm_password = request.form['confirmPassword']
        keyword = request.form.get('keyword')

        if password != confirm_password:
            return "Passwords do not match"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users_general (student_id, name, username, email, password, keyword, role, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
                           (student_id, name, username, email, generate_password_hash(password), keyword, 'user'))
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
    return render_template('eventregsys.html', event=event)


@app.route('/form', methods=['GET', 'POST'])
def form():
    event_id = request.args.get('event_id', 1)
    return render_template('form.html', event_id=event_id)

@app.route('/register', methods=['POST'])
def register_event():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data received"
        }), 400

    print("Data received:", data)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
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
    conn.close()

    return redirect(url_for('eventregister'))


@app.route('/createevent', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        event_name = request.form['Event_name']
        event_description = request.form['Event_description']
        event_date = request.form['Event_date']
        event_time = request.form['Event_time']
        event_location = request.form['Event_location']

        username = session.get('user')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT student_id FROM users_general WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            return "User not found"

        student_id = user["student_id"]

        cursor.execute("""
            INSERT INTO events
            (event_name, description, date, time, location, student_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_name, event_description, event_date,
              event_time, event_location, student_id))

        conn.commit()
        conn.close()

        return redirect(url_for('eventbrowsing'))

    return render_template('create_event.html')

@app.route('/user_dashboard1')
def dashboard():
    return render_template('user_dashboard1.html')

@app.route('/UserProfile')
def user_profile():
    return render_template('UserProfile.html')

@app.route("/cancel_event/<int:event_id>")
def cancel_event(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT event_id, event_name, description, date, time, location
        FROM events
        WHERE event_id = ?
    """, (event_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Event not found"

    event = {
        "id": row["event_id"],
        "name": row["event_name"],
        "desc": row["description"],
        "date": row["date"],
        "time": row["time"],
        "venue": row["location"]
    }

    return render_template("cancelreg.html", event=event, event_id=event_id)

@app.route("/cancel_registration/<int:event_id>", methods=["POST"])
def cancel_registration(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ⚠️ You likely need a proper table for registrations with event_id
    cursor.execute("""
        DELETE FROM event_registrations
        WHERE id = ?
    """, (event_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)

