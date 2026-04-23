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
    bio TEXT,
    birthday DATE,
    faculty TEXT,
    year_of_study INTEGER,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

CREATE TABLE organizer_details (
    student_id VARCHAR(10) PRIMARY KEY,
    club_body TEXT NOT NULL,
    position_title TEXT NOT NULL,
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

INSERT INTO users_general (student_id, name, username, email, password, role)
VALUES ('S001', 'Ali', 'ali123', 'ali@email.com', 'pass123', 'user');

INSERT INTO user_details (student_id, bio, birthday, faculty, year_of_study)
VALUES ('S001', 'I love coding', '2003-05-01', 'Science', 2);

INSERT INTO organizer_details (student_id, club_body, position_title)
VALUES ('S002', 'Drama Club', 'President');

SELECT * FROM users_general;
SELECT * FROM user_details;
SELECT * FROM organizer_details;