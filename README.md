# 🎓 University Course Management System
### Database Lab Project | Flask + SQLite + Python

---

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?style=flat-square&logo=sqlite)
![HTML](https://img.shields.io/badge/HTML5-CSS3-orange?style=flat-square&logo=html5)

**A fully functional web-based university course management system with role-based access control.**

</div>

---

## 📋 Overview

The University Course Management System (UCMS) is a web application built with **Flask** and **SQLite** that allows universities to manage students, instructors, courses, and enrollments through a clean, modern interface.

The UI theme follows the **IT Issue Management System** design language:
- 🔴 Primary Red: `#9E1124`
- 🟢 Primary Teal: `#144F4D`

---

## 🗂️ Project Structure

```
UniversityCMS/
│
├── app.py                        ← Main Flask application (all routes)
├── init_db.py                    ← Database initializer with sample data
├── schema.sql                    ← Database schema (tables + seed data)
├── requirements.txt              ← Python dependencies (just flask)
├── database.db                   ← SQLite database (auto-generated)
│
├── static/
│   └── css/
│       └── style.css             ← Full theme stylesheet
│
└── templates/
    ├── base.html                 ← Master layout (sidebar + topbar)
    ├── login.html                ← Login page with role selector
    │
    ├── dashboard_admin.html      ← Admin dashboard
    ├── dashboard_instructor.html ← Instructor dashboard
    ├── dashboard_student.html    ← Student dashboard
    │
    ├── admin_users.html          ← View all users
    ├── admin_add_user.html       ← Add new user form
    ├── admin_courses.html        ← View all courses
    ├── admin_add_course.html     ← Add new course form
    ├── admin_students.html       ← View all students
    ├── admin_enrollments.html    ← View all enrollments
    │
    ├── instructor_courses.html       ← Instructor's assigned courses
    ├── instructor_students.html      ← Students in a specific course + grading
    ├── instructor_all_students.html  ← All students across all courses
    │
    ├── student_courses.html      ← Browse & enroll in courses
    ├── student_grades.html       ← View grades + GPA
    └── student_profile.html      ← Student profile info
```

---

## 🗄️ Database Design

### Tables

| Table | Description |
|---|---|
| `User` | All system accounts (admin, student, instructor) |
| `Student` | Student profile linked to User |
| `Instructor` | Instructor profile linked to User |
| `Course` | Courses with credits, department, instructor |
| `Enrollment` | Student-Course relationship with grade and semester |

### Entity Relationships

```
User ──────── Student ──────── Enrollment ──────── Course ──────── Instructor
         1:1            1:N              N:1              N:1
```

### Schema Summary

```sql
User        (user_id, username, email, password, role)
Student     (student_id, name, email, department, user_id)
Instructor  (instructor_id, name, email, department, user_id)
Course      (course_id, course_name, credits, department, instructor_id)
Enrollment  (enrollment_id, student_id, course_id, semester, grade, status)
```

---

## 👥 Roles & Permissions

| Feature | Admin | Instructor | Student |
|---|:---:|:---:|:---:|
| View Dashboard | ✅ | ✅ | ✅ |
| Add / Delete Users | ✅ | ❌ | ❌ |
| Add / Delete Courses | ✅ | ❌ | ❌ |
| View All Students | ✅ | ✅ (own courses) | ❌ |
| View All Enrollments | ✅ | ❌ | ❌ |
| Assign Grades | ❌ | ✅ | ❌ |
| Enroll in Courses | ❌ | ❌ | ✅ |
| Drop Courses | ❌ | ❌ | ✅ |
| View Own Grades | ❌ | ❌ | ✅ |
| View Own Profile | ❌ | ❌ | ✅ |

---

## ⚙️ Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.8 or higher |
| pip | Latest |
| Flask | 2.x (auto-installed) |
| SQLite | Built into Python |
| Web Browser | Any modern browser |

> **No MySQL, no XAMPP, no external database needed.** SQLite is built into Python.

---

## 🚀 Setup & Run (Step by Step)

### Step 1 — Download & Extract
Extract the project ZIP and open the folder in your terminal / CMD.

```bash
cd path/to/UniversityCMS
```

### Step 2 — Install Flask

```bash
pip install flask
```

### Step 3 — Initialize the Database

```bash
python init_db.py
```

You should see:
```
✅ Database created successfully!

Default login credentials:
  Admin     : admin@university.edu  / admin123
  Instructor: smith@university.edu  / pass123
  Student   : john@university.edu   / pass123
```

### Step 4 — Run the Application

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 5 — Open in Browser

```
http://127.0.0.1:5000
```

---

## 🔐 Default Login Credentials

| Role | Email | Password |
|---|---|---|
| 👑 Admin | admin@university.edu | admin123 |
| 👨‍🏫 Instructor | smith@university.edu | pass123 |
| 🎓 Student | john@university.edu | pass123 |

---

## ✅ Features by Role

### 👑 Admin
- View system-wide dashboard with total students, instructors, courses, enrollments
- Add new users (students, instructors, or admins)
- Delete users from the system
- Add new courses and assign instructors
- Delete courses
- View all student records
- View all enrollment records across the university

### 👨‍🏫 Instructor
- View personal dashboard with course and student statistics
- View all assigned courses
- View students enrolled in each course
- Assign and update grades (scale: 0.0 – 4.0)
- View all students across all teaching courses

### 🎓 Student
- View personal dashboard with enrolled courses and GPA
- Browse all available courses
- Enroll in courses by selecting semester
- Drop courses (only if not yet graded)
- View grades with letter grade and GPA calculation
- View personal profile

---

## 🎨 UI Design

| Element | Detail |
|---|---|
| Font | DM Sans + Sora (Google Fonts) |
| Primary Color | `#9E1124` (Red) |
| Secondary Color | `#144F4D` (Teal) |
| Background | `#F4F6F9` |
| Cards | White with subtle shadow + colored accent bar |
| Sidebar | Teal gradient with active item in Red |
| Badges | Color-coded by role and status |
| Grade Pills | Color-coded A/B/C/D/F |
| Layout | Fixed sidebar + sticky topbar + scrollable content |

---

## 📁 Key Files Explained

### `app.py`
The entire Flask backend. Contains:
- Route definitions for all 3 roles
- Session management and login/logout
- Auth guards (`login_required`, `role_required` decorators)
- All database query logic using `sqlite3`

### `schema.sql`
Defines all 5 tables with proper foreign keys, constraints, and sample seed data. Run once via `init_db.py`.

### `init_db.py`
Drops and recreates the database from scratch using `schema.sql`. Re-run this anytime to reset to default data.

### `static/css/style.css`
Complete stylesheet — no external CSS frameworks used. Everything is custom-built matching the IT Issue Management System theme.

### `templates/base.html`
Master Jinja2 template. All other pages extend this. Contains the sidebar, topbar, flash message display, and role-based navigation rendering.

---

## 🔄 How Grading Works

```
Student enrolls in course
        ↓
Enrollment created with grade = NULL
        ↓
Instructor assigns grade (0.0 – 4.0)
        ↓
Enrollment status → "completed"
        ↓
Student can view grade + updated GPA
        ↓
Student CANNOT drop a graded course
```

**GPA Calculation:**
```
GPA = Sum of all grades / Number of graded courses
```

**Letter Grade Scale:**
| GPA | Letter |
|---|---|
| 3.5 – 4.0 | A |
| 3.0 – 3.4 | B |
| 2.0 – 2.9 | C |
| 1.0 – 1.9 | D |
| 0.0 – 0.9 | F |

---

## ⚠️ Common Issues & Fixes

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask` | Run `pip install flask` |
| `database.db not found` | Run `python init_db.py` first |
| `TemplateNotFound` error | Make sure you're running `app.py` from the root `UniversityCMS/` folder |
| Login says invalid credentials | Run `python init_db.py` to reset the database |
| Port 5000 already in use | Change port: `app.run(port=5001)` in `app.py` |
| Changes not reflecting | Hard refresh browser: `Ctrl + Shift + R` |

---

## 🛠️ How to Reset the Database

If you want to start fresh with default data:

```bash
python init_db.py
```

> ⚠️ This deletes all existing data and recreates everything from scratch.

---

## 🧪 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask |
| Database | SQLite 3 (via Python `sqlite3` module) |
| Frontend | HTML5 + CSS3 (custom, no Bootstrap) |
| Templating | Jinja2 (Flask built-in) |
| Fonts | Google Fonts (DM Sans, Sora) |
| Icons | Unicode Emoji |

---

## 👨‍💻 Developer Notes

- The app runs in **debug mode** by default (`app.run(debug=True)`). Disable this for any production deployment.
- Passwords are stored in **plain text** for simplicity. In a real system, use `bcrypt` or `werkzeug.security`.
- The `session` stores `user_id`, `role`, `name`, `email`, and `profile_id` after login.
- All routes are protected with `@login_required` and `@role_required` decorators.
- `conn.row_factory = sqlite3.Row` is used so query results are accessible by column name (`row['email']`) not just index.

---

*University Course Management System — Database Lab Project*
