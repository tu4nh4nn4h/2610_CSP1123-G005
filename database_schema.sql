-- SQLite
CREATE TABLE IF NOT EXISTS users_general (
    student_email TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    student_id VARCHAR(10) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    keyword TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin'))
);

CREATE TABLE IF NOT EXISTS user_details (
    student_email TEXT PRIMARY KEY,
    bio TEXT,
    email_personal TEXT,
    birthday DATE,
    faculty TEXT,
    year_of_study INTEGER,
    FOREIGN KEY (student_email) REFERENCES users_general(student_email)
);

CREATE TABLE IF NOT EXISTS organizer_details (
    student_email TEXT PRIMARY KEY,
    club_body TEXT NOT NULL,
    position_title TEXT NOT NULL,
    FOREIGN KEY (student_email) REFERENCES users_general(student_email)
);

CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location TEXT NOT NULL,
    student_email TEXT NOT NULL,
    FOREIGN KEY (student_email) REFERENCES organizer_details(student_email)
);

CREATE TABLE IF NOT EXISTS event_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS event_tag_map (
    event_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (tag_id) REFERENCES event_tags(tag_id),
    PRIMARY KEY(event_id, tag_id)
);

CREATE TABLE IF NOT EXISTS event_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id VARCHAR(10) NOT NULL,
    student_email TEXT NOT NULL,
    personal_email TEXT,
    phone_number TEXT NOT NULL,
    faculty TEXT NOT NULL,
    FOREIGN KEY (student_email) REFERENCES users_general(student_email)
);

SELECT * FROM users_general;
SELECT * FROM user_details;
SELECT * FROM organizer_details;
SELECT * FROM events;
SELECT * FROM event_tags;
SELECT * FROM event_tag_map;
SELECT * FROM event_registrations;