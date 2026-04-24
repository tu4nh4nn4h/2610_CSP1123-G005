from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "your_secret_key"

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/change_email', methods=['POST'])
def change_email():
    # Implementation for changing email
    pass

def get_database_connection():
    connection = sqlite3.connect('database.db')  # your database file
    connection.row_factory = sqlite3.Row       # access columns by name
    return connection

def setup_database():
    conn = get_database_connection()
    cursor = conn.cursor()

    # users_general table 
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_general (
                        student_id VARCHAR(10) PRIMARY KEY,
                        name TEXT NOT NULL,
                        username VARCHAR(50) NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        password VARCHAR(50) NOT NULL,
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

@app.route('/')
def home():
    return render_template('home.html')
    


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = username  # Assuming the first column is user ID
            return redirect(url_for('eventbrowsing'))
        else:
            return "Invalid username or password"
        # Handle sign-in logic here
        pass
     
    return render_template('signin.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['Name']
        email = request.form['Email']
        username = request.form['Username']
        student_id = request.form['Student_id']
        password = request.form['Password']
        password_confirm = request.form['confirmPassword']
        # Handle registration logic here
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users_general (student_id, name, username, email, password, role) VALUES (?, ?, ?, ?, ?, ?)",
                           (student_id, name, username, email, generate_password_hash(password), 'user'))
            conn.commit()
        except:
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
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        pass
    return render_template('register_organizer.html')

@app.route('/change_password', methods=['POST'])
def change_password():
    # Implementation for changing password
    current = request.form['current_password']
    new = request.form['new_password']
    confirm = request.form['confirm_password']

    user_id = session.get('username')  # Assuming username is stored in session

    conn = sqlite3.connect('database.db')
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

@app.route('/eventbrowsing')
def eventbrowsing():
    return render_template('eventdisbrow.html')

@app.route('/eventregister')
def eventregister():
    return render_template('eventregsys.html')

@app.route('/event')
def event_page():
    return render_template('eventregsys.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Handle form submission logic here
        pass
    return render_template('form.html') # show the form

if __name__ == "__main__":
    setup_database()  # Ensure database is set up before running the app
    app.run(debug=True)