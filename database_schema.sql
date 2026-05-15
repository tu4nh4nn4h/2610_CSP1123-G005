-- SQLite
-- 1. Main User Table
CREATE TABLE IF NOT EXISTS users_general (
    student_id varchar(10) PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    keyword TEXT,
    role TEXT NOT NULL CHECK(role IN ('user', 'organizer', 'admin')),
    is_verified INTEGER DEFAULT 0
);

-- 2. User Details (Profiles)
CREATE TABLE IF NOT EXISTS user_details (
    student_id VARCHAR(10) PRIMARY KEY,
    bio TEXT,
    birthday DATE,
    faculty TEXT,
    year_of_study INTEGER,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

-- 3. Organizer Details
CREATE TABLE IF NOT EXISTS organizer_details (
    student_id VARCHAR(10) PRIMARY KEY,
    club_body TEXT NOT NULL,
    position_title TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

-- 4. Events
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES organizer_details(student_id)
);

-- 5. Event Tags (No change needed here)
CREATE TABLE IF NOT EXISTS event_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT UNIQUE NOT NULL
);

-- 6. Event Tag Mapping (No change needed here)
CREATE TABLE IF NOT EXISTS event_tag_map (
    event_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (tag_id) REFERENCES event_tags(tag_id),
    PRIMARY KEY(event_id, tag_id)
);

-- 7. Event Registrations
CREATE TABLE IF NOT EXISTS event_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id VARCHAR(10) NOT NULL, -- Now links directly to the PK of users_general
    email TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    faculty TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

SELECT * FROM users_general;
SELECT * FROM user_details;
SELECT * FROM organizer_details;
SELECT * FROM events;
SELECT * FROM event_tags;
SELECT * FROM event_tag_map;
SELECT * FROM event_registrations;