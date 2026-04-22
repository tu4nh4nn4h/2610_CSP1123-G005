-- SQLite
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password VARCHAR(14) NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin'))
);

CREATE TABLE user_details (
    user_id INTEGER PRIMARY KEY ,
    student_id VARCHAR(10) NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE organizer_details (
    user_id INTEGER PRIMARY KEY,
    student_id VARCHAR(10) NOT NULL UNIQUE,
    phone_number INTEGEREGER NOT NULL,
    club_body TEXT NOT NULL,
    position TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);



