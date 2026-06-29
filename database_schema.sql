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
    is_verified INTEGER DEFAULT 0,
    pending_email TEXT,
    security_question TEXT
);

-- 2. User Details (Profiles)
CREATE TABLE IF NOT EXISTS user_details (
    student_id VARCHAR(10) PRIMARY KEY,
    bio TEXT,
    birthday DATE,
    faculty TEXT,
    year_of_study INTEGER,
    profile_picture TEXT,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

-- 3. Organizer Details
CREATE TABLE IF NOT EXISTS organizer_details (
    student_id VARCHAR(10) PRIMARY KEY,
    club_body TEXT NOT NULL,
    position_title TEXT NOT NULL,
    proof_document TEXT,
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

-- 4. Events
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_poster TEXT,                   -- new column for event poster URL/path
    event_name TEXT NOT NULL,
    event_description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    event_mode TEXT NOT NULL CHECK(event_mode IN ('online', 'offline', 'hybrid')),
    main_location TEXT NOT NULL,         -- corresponds to id="mainloc"
    general_location TEXT,               -- optional, only for general locations
    faculty_wing TEXT,                   -- optional, only for faculty path
    specific_location TEXT,              -- optional, only for faculty path
    participation_option TEXT NOT NULL CHECK(participation_option IN ('unlimited', 'limited')),
    limited_max_participants INTEGER,    -- optional, only for limited participation
    event_link TEXT,
    student_id varchar(10) NOT NULL,
    event_status TEXT DEFAULT 'Pending' CHECK(event_status IN ('Pending', 'Approved', 'Redo')),
    admin_remark TEXT,
    edit_attempt INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES organizer_details(student_id)
);

-- 5. Event Registrations
CREATE TABLE IF NOT EXISTS event_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    student_id VARCHAR(10) NOT NULL, -- Now links directly to the PK of users_general
    email TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    faculty TEXT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

-- 6. Notifications triggered by user action
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id varchar(10) NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    link TEXT,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);

-- 7. Organizer applications
CREATE TABLE IF NOT EXISTS organizer_applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(10) NOT NULL,
    club_body TEXT NOT NULL,
    position_title TEXT NOT NULL,
    proof_document TEXT NOT NULL,
    application_status TEXT NOT NULL DEFAULT 'Pending' CHECK(application_status IN ('Pending', 'Approved', 'Rejected')),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rejected_date DATE,
    FOREIGN KEY (student_id) REFERENCES users_general(student_id)
);


SELECT * FROM users_general;
SELECT * FROM user_details;
SELECT * FROM organizer_details;
SELECT * FROM events;
SELECT * FROM event_registrations;
SELECT * FROM notifications;
SELECT * FROM organizer_applications;