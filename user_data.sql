-- SQLite
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username varchar(50) NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password varchar(14) NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin'))
);

CREATE TABLE user_details (
    user_id INT PRIMARY KEY ,
    student_id VARCHAR(10) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ;

CREATE TABLE organizer_details (


