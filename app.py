from flask import Flask, render_template
import sqlite3
app = Flask(__name__)

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

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('eventdisbrow.html')

@app.route('/register')
def register():
    return render_template('eventregsys.html')

if __name__ == "__main__":
    setup_database()  # Ensure database is set up before running the app
    app.run(debug=True)