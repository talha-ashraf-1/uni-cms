-- ============================================================
-- University Course Management System - Database Schema
-- ============================================================

DROP TABLE IF EXISTS Enrollment;
DROP TABLE IF EXISTS Course;
DROP TABLE IF EXISTS Professor;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS User;

CREATE TABLE User (
    user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT UNIQUE NOT NULL,
    email     TEXT UNIQUE NOT NULL,
    password  TEXT NOT NULL,
    role      TEXT NOT NULL CHECK(role IN ('admin', 'student', 'instructor')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE Student (
    student_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    department  TEXT,
    user_id     INTEGER UNIQUE,
    FOREIGN KEY(user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Instructor (
    instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    department    TEXT,
    user_id       INTEGER UNIQUE,
    FOREIGN KEY(user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Course (
    course_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    credits     INTEGER NOT NULL DEFAULT 3,
    department  TEXT,
    instructor_id INTEGER,
    created_at  TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(instructor_id) REFERENCES Instructor(instructor_id) ON DELETE SET NULL
);

CREATE TABLE Enrollment (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL,
    course_id     INTEGER NOT NULL,
    semester      TEXT NOT NULL,
    grade         REAL DEFAULT NULL,
    status        TEXT DEFAULT 'enrolled' CHECK(status IN ('enrolled','completed','dropped')),
    enrolled_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(student_id, course_id, semester),
    FOREIGN KEY(student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY(course_id)  REFERENCES Course(course_id)  ON DELETE CASCADE
);

-- ============================================================
-- Default seed data
-- ============================================================

-- Admin account (password: admin123)
INSERT INTO User (username, email, password, role) VALUES
    ('admin', 'admin@university.edu', 'admin123', 'admin');

-- Sample instructor user
INSERT INTO User (username, email, password, role) VALUES
    ('drsmith', 'smith@university.edu', 'pass123', 'instructor');
INSERT INTO Instructor (name, email, department, user_id) VALUES
    ('Dr. Smith', 'smith@university.edu', 'Computer Science', 2);

-- Sample student user
INSERT INTO User (username, email, password, role) VALUES
    ('john_doe', 'john@university.edu', 'pass123', 'student');
INSERT INTO Student (name, email, department, user_id) VALUES
    ('John Doe', 'john@university.edu', 'Computer Science', 3);

-- Sample courses
INSERT INTO Course (course_name, credits, department, instructor_id) VALUES
    ('Data Structures', 3, 'Computer Science', 1),
    ('Database Systems', 3, 'Computer Science', 1),
    ('Operating Systems', 3, 'Computer Science', 1);

-- Sample enrollment
INSERT INTO Enrollment (student_id, course_id, semester) VALUES (1, 1, 'Fall 2025');
