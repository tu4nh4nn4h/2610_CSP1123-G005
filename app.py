from ast import keyword
from datetime import date
from os import name

from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "your_secret_key"

def get_db_connection():                     # helper function to get a database connection
    conn = sqlite3.connect('database.db')    # your database file
    conn.row_factory = sqlite3.Row           # access columns by name
    conn.execute("PRAGMA foreign_keys = 1")  # enable foreign keys connection between tables
    return conn

def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # users_general table 
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_general (
                        student_id VARCHAR(10) PRIMARY KEY,
                        name TEXT NOT NULL,
                        username VARCHAR(50) NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        password VARCHAR(50) NOT NULL,
                        keyword TEXT,
                        role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin'))
                     )''')

    # user_details table
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_details (
                        student_id VARCHAR(10) PRIMARY KEY,
                        bio TEXT,
                        birthday DATE,
                        faculty TEXT,
                        year_of_study INTEGER,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                     )''')

    # organizer_details table
    cursor.execute('''CREATE TABLE IF NOT EXISTS organizer_details (
                        student_id VARCHAR(10) PRIMARY KEY,
                        club_body TEXT NOT NULL,
                        position_title TEXT NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                     )''')

    # events table
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        date DATE NOT NULL,
                        time TIME NOT NULL,
                        location TEXT NOT NULL,
                        student_id VARCHAR(10) NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES organizer_details(student_id)
                     )''')

    # event_tags table
    cursor.execute('''CREATE TABLE IF NOT EXISTS event_tags (
                        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tag_name TEXT UNIQUE NOT NULL
                     )''')

    # event_tag_map table
    cursor.execute('''CREATE TABLE IF NOT EXISTS event_tag_map (
                        event_id INTEGER NOT NULL,
                        tag_id INTEGER NOT NULL,
                        FOREIGN KEY (event_id) REFERENCES events(event_id),
                        FOREIGN KEY (tag_id) REFERENCES event_tags(tag_id),
                        PRIMARY KEY(event_id, tag_id)
                     )''')
    
    # event_registrations table
    cursor.execute('''CREATE TABLE IF NOT EXISTS event_registrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        student_id VARCHAR(10) NOT NULL,
                        student_email TEXT NOT NULL,
                        personal_email TEXT,
                        phone_number TEXT NOT NULL,
                        faculty TEXT NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES users_general(student_id)
                    )''')

    conn.commit()
    conn.close()

# Route for home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for user login
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
              
            if check_password_hash(stored_password, password):
                session['user'] = username  # Assuming the first column is user ID
                return redirect(url_for('eventbrowsing'))
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
        # Here you would typically check the keyword against a stored value
        # For now, we'll just simulate a successful verification
        session['reset_user'] = username  # Store the username in session for password reset
        return redirect(url_for('reset_password'))
    else:
        return "Invalid username or keyword"

# Route for password reset
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_user' not in session:
        return redirect(url_for('signin'))
    
    if request.method == 'POST':
        NewPassword = request.form.get('NewPassword')
        ConfirmPassword = request.form.get('ConfirmNewPassword')

        if NewPassword != ConfirmPassword:
            return "Passwords do not match"
    
        username = session['reset_user']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
        "UPDATE users_general SET password = ? WHERE username = ?", (generate_password_hash(NewPassword), username))
    
        conn.commit()
        conn.close()
        session.pop('reset_user', None)  # Clear the reset user from session
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
        password_confirm = request.form['confirmPassword']
        keyword = request.form['keyword']

        if password != password_confirm:
            return "Passwords do not match"
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users_general (student_id, name, username, email, password, keyword, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (student_id, name, username, email, generate_password_hash(password), keyword, 'user'))
            conn.commit()

        except sqlite3.IntegrityError:
            return "username or email already exists"
        finally:
            conn.close()

        return redirect(url_for('signin'))
        
    return render_template('register.html')

@app.route('/register_organizer', methods=['GET', 'POST'])
def register_organizer():
    if request.method == 'POST':
        name = request.form['Name']
        email = request.form['Email']
        username = request.form['Username']
        student_id = request.form['Student_id']
        password = request.form['Password']
        password_confirm = request.form['confirmPassword']
        club_body = request.form['Club_body']
        position_title = request.form['Position_title']
        # Handle organizer registration logic here
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users_general (student_id, name, username, email, password, keyword, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (student_id, name, username, email, generate_password_hash(password), keyword, 'organizer'))
            cursor.execute("INSERT INTO organizer_details (student_id, club_body, position_title) VALUES (?, ?, ?)",
                           (student_id, club_body, position_title))
            conn.commit()
        except sqlite3.IntegrityError: #catch errors if the username/email already exists.
            return "username or email already exists"
        finally:
            conn.close()
            
        return redirect(url_for('signin'))
    return render_template('register_organizer.html')

@app.route('/change_password', methods=['POST'])
def change_password():
    # Implementation for changing password
    current = request.form['current_password']
    new = request.form['new_password']
    confirm = request.form['confirm_password']

    user_id = session.get('username')  # Assuming username is stored in session

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users_general WHERE username = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        db_password = result[0]
        if not check_password_hash(db_password, current):
            return "Current password is incorrect"
        if new != confirm:
            return "New password and confirm password do not match"
        cursor.execute("UPDATE users_general SET password = ? WHERE username = ?", (generate_password_hash(new), user_id))
        conn.commit()
        conn.close()
        return "Password updated successfully"
    else:
        return "User not found"
    return render_template('EditProfile.html')

@app.route('/change_email', methods=['POST'])
def change_email():
    # Implementation for changing email
    pass

@app.route('/eventbrowsing')
def eventbrowsing():
    return render_template('EventDisBrow.html')

@app.route('/eventregister')
def eventregister():
    return render_template('eventregsys.html')

@app.route('/event')
def event_page():
    return render_template('eventregsys.html')

@app.route('/event/<int:event_id>')
def event_detail(event_id):

    # events = {
    #     1: {
    #         "name": "Hackathon 2026",
    #         "desc": "Step into the ultimate innovation challenge where creativity meets technology. Team up with friends, solve real-world problems, and bring your ideas to life in just hours. Whether you're a coding pro or a beginner, this is your chance to learn, compete, and win exciting prizes while pushing your limits.",
    #         "date": "20 May 2026",
    #         "time": "10:00 AM - 6:00 PM",
    #         "venue": "Dewan Tun Canselor, MMU Cyberjaya"
    #     },
    #     2: {
    #         "name": "Food Festival 2026",
    #         "desc": "Get ready to indulge in a vibrant celebration of flavors from around the world. From local street food to trendy bites, explore a variety of delicious treats while enjoying music, games, and a lively atmosphere. Bring your friends and experience a day full of fun, food, and unforgettable moments.",
    #         "date": "25 May 2026",
    #         "time": "10:00 AM - 10:00 PM",
    #         "venue": "Central Plaza, MMU Cyberjaya"
    #     },
    #     3: {
    #         "name": "MMU Fun Run 2026",
    #         "desc": "Lace up your shoes and join an energetic run filled with excitement, music, and great vibes. Whether you're running to win or just for fun, enjoy a refreshing experience with friends while staying active. Celebrate fitness, laughter, and community in an event that’s all about good energy and great memories.",
    #         "date": "30 May 2026",
    #         "time": "8:00 AM - 5:00 PM",
    #         "venue": "Stadium MMU Cyberjaya"
    #     },
    #     4: {
    #         "name": "MMU Career Talk 2026",
    #         "desc": "Discover real insights from industry professionals and uncover the opportunities waiting beyond campus life. Gain practical advice, explore career pathways, and connect with experts who can shape your future. Don’t miss this chance to get inspired, build confidence, and take the first step toward your dream career.",
    #         "date": "27 June 2026",
    #         "time": "10:00 AM - 4:00 PM",
    #         "venue": "CNMX1005 CLC, MMU Cyberjaya"
    #     }
    # }

    # event = events.get(event_id)
    # return render_template('eventregsys.html', event=event)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event = cursor.fetchone()

    conn.close()

    return render_template('eventregsys.html', event=event, event_id=event_id)

@app.route('/form', methods=['GET', 'POST'])
def form():
<<<<<<< HEAD
=======
    event_id = request.args.get('event_id')
    return render_template('form.html', event_id=event_id)
>>>>>>> 7af0a8a47ee0ca9ad3fb3545b32afc6c08f03bda
    if request.method == 'POST':
        name = request.form['Name']
        student_email = request.form['Student_email']
        personal_email = request.form['Personal_email']
        phone_number = request.form['Phone_number']
        student_id = request.form['Student_id']

        # Handle registration logic here
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO event_registrations (student_id, name, student_email, personal_email, phone_number) VALUES (?, ?, ?, ?, ?)",
                           (student_id, name, student_email, personal_email, phone_number))
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for('eventregister'))
<<<<<<< HEAD

    event_id = request.args.get('event_id')
    return render_template('form.html', event_id=event_id)
=======
    return render_template('form.html') # show the form
>>>>>>> 7af0a8a47ee0ca9ad3fb3545b32afc6c08f03bda

@app.route('/createevent', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        event_name = request.form['Event_name']
        event_description = request.form['Event_description']
        event_date = request.form['Event_date']
        event_time = request.form['Event_time']
        event_location = request.form['Event_location']

        # Handle registration logic here
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO events (event_name, description, date, time, location) VALUES (?, ?, ?, ?, ?)",
                           (event_name, event_description, event_date, event_time, event_location))
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for('eventbrowsing'))
    return render_template('create_event.html') # show the form

if __name__ == "__main__":
    setup_database()  # Ensure database is set up before running the app
    app.run(debug=True)