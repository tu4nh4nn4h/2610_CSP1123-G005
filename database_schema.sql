-- SQLite
CREATE TABLE users_general (
    student_id VARCHAR(10) PRIMARY KEY,
    name TEXT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin'))
);

CREATE TABLE user_details (
    student_id VARCHAR(10) PRIMARY KEY,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

CREATE TABLE organizer_details (
    student_id VARCHAR(10) PRIMARY KEY,
    club_body TEXT NOT NULL,
    position/title TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

CREATE TABLE organizer_details (
    student_id VARCHAR(10) PRIMARY KEY,
    club_body TEXT NOT NULL,
    position/title TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location TEXT NOT NULL,
    student_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES organizer_details(student_id)
);

CREATE TABLE event_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT UNIQUE NOT NULL
);

CREATE TABLE event_tag_map (
    event_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (tag_id) REFERENCES event_tags(tag_id),
    PRIMARY KEY(event_id, tag_id)
);
