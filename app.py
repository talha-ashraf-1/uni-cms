from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ucms_secret_key_2024"
DB_PATH = "database.db"

# ── DB Helper ─────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def query(sql, args=(), one=False):
    conn = get_db()
    cur  = conn.execute(sql, args)
    rv   = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute(sql, args=()):
    conn = get_db()
    try:
        conn.execute(sql, args)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return str(e)

# ── Auth Guards ───────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                flash("Access denied.", "error")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password'].strip()
        role     = request.form['role'].strip()

        user = query(
            "SELECT * FROM User WHERE email=? AND password=? AND role=?",
            (email, password, role), one=True
        )
        if user:
            session['user_id']  = user['user_id']
            session['username'] = user['username']
            session['email']    = user['email']
            session['role']     = user['role']

            # Get profile id (student_id / instructor_id)
            if role == 'student':
                p = query("SELECT student_id, name FROM Student WHERE user_id=?",
                          (user['user_id'],), one=True)
                if p:
                    session['profile_id'] = p['student_id']
                    session['name']       = p['name']
            elif role == 'instructor':
                p = query("SELECT instructor_id, name FROM Instructor WHERE user_id=?",
                          (user['user_id'],), one=True)
                if p:
                    session['profile_id'] = p['instructor_id']
                    session['name']       = p['name']
            else:
                session['name'] = 'Administrator'

            flash(f"Welcome back, {session.get('name', email)}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email, password, or role.", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    role = session['role']
    stats = {}

    if role == 'admin':
        stats['students']    = query("SELECT COUNT(*) as c FROM Student", one=True)['c']
        stats['instructors'] = query("SELECT COUNT(*) as c FROM Instructor", one=True)['c']
        stats['courses']     = query("SELECT COUNT(*) as c FROM Course", one=True)['c']
        stats['enrollments'] = query("SELECT COUNT(*) as c FROM Enrollment", one=True)['c']
        recent_users = query("SELECT * FROM User ORDER BY created_at DESC LIMIT 5")
        return render_template('dashboard_admin.html', stats=stats, recent_users=recent_users)

    elif role == 'instructor':
        iid = session.get('profile_id')
        stats['my_courses']  = query("SELECT COUNT(*) as c FROM Course WHERE instructor_id=?", (iid,), one=True)['c']
        stats['my_students'] = query(
            "SELECT COUNT(DISTINCT e.student_id) as c FROM Enrollment e "
            "JOIN Course c ON e.course_id=c.course_id WHERE c.instructor_id=?", (iid,), one=True)['c']
        stats['pending_grades'] = query(
            "SELECT COUNT(*) as c FROM Enrollment e "
            "JOIN Course c ON e.course_id=c.course_id "
            "WHERE c.instructor_id=? AND e.grade IS NULL", (iid,), one=True)['c']
        my_courses = query(
            "SELECT c.*, COUNT(e.enrollment_id) as enrolled "
            "FROM Course c LEFT JOIN Enrollment e ON c.course_id=e.course_id "
            "WHERE c.instructor_id=? GROUP BY c.course_id", (iid,))
        return render_template('dashboard_instructor.html', stats=stats, my_courses=my_courses)

    else:  # student
        sid = session.get('profile_id')
        stats['enrolled']  = query("SELECT COUNT(*) as c FROM Enrollment WHERE student_id=?", (sid,), one=True)['c']
        stats['completed'] = query("SELECT COUNT(*) as c FROM Enrollment WHERE student_id=? AND grade IS NOT NULL", (sid,), one=True)['c']
        enrollments = query(
            "SELECT e.*, c.course_name, c.credits, c.department, "
            "i.name as instructor_name "
            "FROM Enrollment e "
            "JOIN Course c ON e.course_id=c.course_id "
            "LEFT JOIN Instructor i ON c.instructor_id=i.instructor_id "
            "WHERE e.student_id=? ORDER BY e.enrolled_at DESC", (sid,))
        # GPA
        graded = [e for e in enrollments if e['grade'] is not None]
        gpa = round(sum(e['grade'] for e in graded) / len(graded), 2) if graded else None
        return render_template('dashboard_student.html', stats=stats, enrollments=enrollments, gpa=gpa)

# ── Admin: Users ──────────────────────────────────────────────────────────────

@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    users = query("SELECT * FROM User ORDER BY role, username")
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_add_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password'].strip()
        role     = request.form['role'].strip()
        name     = request.form['name'].strip()
        dept     = request.form['department'].strip()

        # Check email uniqueness
        exists = query("SELECT 1 FROM User WHERE email=? OR username=?", (email, username), one=True)
        if exists:
            flash("Email or username already exists.", "error")
            return redirect(url_for('admin_add_user'))

        result = execute(
            "INSERT INTO User (username, email, password, role) VALUES (?,?,?,?)",
            (username, email, password, role)
        )
        if result is True:
            user = query("SELECT user_id FROM User WHERE email=?", (email,), one=True)
            uid  = user['user_id']
            if role == 'student':
                execute("INSERT INTO Student (name, email, department, user_id) VALUES (?,?,?,?)",
                        (name, email, dept, uid))
            elif role == 'instructor':
                execute("INSERT INTO Instructor (name, email, department, user_id) VALUES (?,?,?,?)",
                        (name, email, dept, uid))
            flash(f"User '{username}' added successfully!", "success")
            return redirect(url_for('admin_users'))
        else:
            flash(f"Error: {result}", "error")

    instructors = query("SELECT * FROM Instructor")
    return render_template('admin_add_user.html')

@app.route('/admin/users/delete/<int:uid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_user(uid):
    if uid == session['user_id']:
        flash("Cannot delete your own account.", "error")
        return redirect(url_for('admin_users'))
    result = execute("DELETE FROM User WHERE user_id=?", (uid,))
    if result is True:
        flash("User deleted.", "success")
    else:
        flash(f"Error: {result}", "error")
    return redirect(url_for('admin_users'))

# ── Admin: Courses ────────────────────────────────────────────────────────────

@app.route('/admin/courses')
@login_required
@role_required('admin')
def admin_courses():
    courses = query(
        "SELECT c.*, i.name as instructor_name, "
        "COUNT(e.enrollment_id) as enrolled "
        "FROM Course c "
        "LEFT JOIN Instructor i ON c.instructor_id=i.instructor_id "
        "LEFT JOIN Enrollment e ON c.course_id=e.course_id "
        "GROUP BY c.course_id ORDER BY c.course_name"
    )
    return render_template('admin_courses.html', courses=courses)

@app.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_add_course():
    if request.method == 'POST':
        name    = request.form['course_name'].strip()
        credits = request.form['credits'].strip()
        dept    = request.form['department'].strip()
        iid     = request.form.get('instructor_id') or None

        result = execute(
            "INSERT INTO Course (course_name, credits, department, instructor_id) VALUES (?,?,?,?)",
            (name, credits, dept, iid)
        )
        if result is True:
            flash(f"Course '{name}' added!", "success")
            return redirect(url_for('admin_courses'))
        else:
            flash(f"Error: {result}", "error")

    instructors = query("SELECT * FROM Instructor ORDER BY name")
    return render_template('admin_add_course.html', instructors=instructors)

@app.route('/admin/courses/delete/<int:cid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_course(cid):
    result = execute("DELETE FROM Course WHERE course_id=?", (cid,))
    flash("Course deleted." if result is True else f"Error: {result}", "success" if result is True else "error")
    return redirect(url_for('admin_courses'))

# ── Admin: Students ───────────────────────────────────────────────────────────

@app.route('/admin/students')
@login_required
@role_required('admin')
def admin_students():
    students = query(
        "SELECT s.*, COUNT(e.enrollment_id) as enrolled "
        "FROM Student s LEFT JOIN Enrollment e ON s.student_id=e.student_id "
        "GROUP BY s.student_id ORDER BY s.name"
    )
    return render_template('admin_students.html', students=students)

# ── Admin: Enrollments ────────────────────────────────────────────────────────

@app.route('/admin/enrollments')
@login_required
@role_required('admin')
def admin_enrollments():
    enrollments = query(
        "SELECT e.*, s.name as student_name, c.course_name, "
        "i.name as instructor_name "
        "FROM Enrollment e "
        "JOIN Student s ON e.student_id=s.student_id "
        "JOIN Course c ON e.course_id=c.course_id "
        "LEFT JOIN Instructor i ON c.instructor_id=i.instructor_id "
        "ORDER BY e.enrolled_at DESC"
    )
    return render_template('admin_enrollments.html', enrollments=enrollments)

# ── Instructor Routes ─────────────────────────────────────────────────────────

@app.route('/instructor/courses')
@login_required
@role_required('instructor')
def instructor_courses():
    iid = session.get('profile_id')
    courses = query(
        "SELECT c.*, COUNT(e.enrollment_id) as enrolled "
        "FROM Course c LEFT JOIN Enrollment e ON c.course_id=e.course_id "
        "WHERE c.instructor_id=? GROUP BY c.course_id", (iid,)
    )
    return render_template('instructor_courses.html', courses=courses)

@app.route('/instructor/course/<int:cid>/students')
@login_required
@role_required('instructor')
def instructor_course_students(cid):
    iid    = session.get('profile_id')
    course = query("SELECT * FROM Course WHERE course_id=? AND instructor_id=?", (cid, iid), one=True)
    if not course:
        flash("Course not found or access denied.", "error")
        return redirect(url_for('instructor_courses'))
    students = query(
        "SELECT e.*, s.name, s.email, s.department "
        "FROM Enrollment e JOIN Student s ON e.student_id=s.student_id "
        "WHERE e.course_id=? ORDER BY s.name", (cid,)
    )
    return render_template('instructor_students.html', course=course, students=students)

@app.route('/instructor/grade', methods=['POST'])
@login_required
@role_required('instructor')
def instructor_grade():
    eid   = request.form['enrollment_id']
    grade = request.form['grade']

    try:
        g = float(grade)
        if not (0.0 <= g <= 4.0):
            flash("Grade must be between 0.0 and 4.0", "error")
            return redirect(request.referrer)
    except ValueError:
        flash("Invalid grade value.", "error")
        return redirect(request.referrer)

    result = execute("UPDATE Enrollment SET grade=?, status='completed' WHERE enrollment_id=?", (g, eid))
    flash("Grade saved!" if result is True else f"Error: {result}",
          "success" if result is True else "error")
    return redirect(request.referrer)

@app.route('/instructor/students')
@login_required
@role_required('instructor')
def instructor_all_students():
    iid = session.get('profile_id')
    students = query(
        "SELECT DISTINCT s.*, c.course_name, e.grade, e.semester "
        "FROM Student s "
        "JOIN Enrollment e ON s.student_id=e.student_id "
        "JOIN Course c ON e.course_id=c.course_id "
        "WHERE c.instructor_id=? ORDER BY s.name", (iid,)
    )
    return render_template('instructor_all_students.html', students=students)

# ── Student Routes ────────────────────────────────────────────────────────────

@app.route('/student/courses')
@login_required
@role_required('student')
def student_courses():
    sid = session.get('profile_id')
    # Available courses (not yet enrolled this semester)
    courses = query(
        "SELECT c.*, i.name as instructor_name, "
        "COUNT(e2.enrollment_id) as enrolled "
        "FROM Course c "
        "LEFT JOIN Instructor i ON c.instructor_id=i.instructor_id "
        "LEFT JOIN Enrollment e2 ON c.course_id=e2.course_id "
        "WHERE c.course_id NOT IN ("
        "  SELECT course_id FROM Enrollment WHERE student_id=? AND semester='Fall 2025'"
        ") GROUP BY c.course_id ORDER BY c.course_name", (sid,)
    )
    return render_template('student_courses.html', courses=courses)

@app.route('/student/enroll/<int:cid>', methods=['POST'])
@login_required
@role_required('student')
def student_enroll(cid):
    sid      = session.get('profile_id')
    semester = request.form.get('semester', 'Fall 2025')

    exists = query(
        "SELECT 1 FROM Enrollment WHERE student_id=? AND course_id=? AND semester=?",
        (sid, cid, semester), one=True
    )
    if exists:
        flash("Already enrolled in this course for this semester.", "error")
        return redirect(url_for('student_courses'))

    result = execute(
        "INSERT INTO Enrollment (student_id, course_id, semester) VALUES (?,?,?)",
        (sid, cid, semester)
    )
    flash("Enrolled successfully!" if result is True else f"Error: {result}",
          "success" if result is True else "error")
    return redirect(url_for('dashboard'))

@app.route('/student/drop/<int:eid>', methods=['POST'])
@login_required
@role_required('student')
def student_drop(eid):
    sid = session.get('profile_id')
    # Verify ownership
    enroll = query("SELECT * FROM Enrollment WHERE enrollment_id=? AND student_id=?", (eid, sid), one=True)
    if not enroll:
        flash("Enrollment not found.", "error")
        return redirect(url_for('dashboard'))
    if enroll['grade'] is not None:
        flash("Cannot drop a graded course.", "error")
        return redirect(url_for('dashboard'))
    execute("DELETE FROM Enrollment WHERE enrollment_id=?", (eid,))
    flash("Course dropped.", "success")
    return redirect(url_for('dashboard'))

@app.route('/student/grades')
@login_required
@role_required('student')
def student_grades():
    sid = session.get('profile_id')
    enrollments = query(
        "SELECT e.*, c.course_name, c.credits, c.department, "
        "i.name as instructor_name "
        "FROM Enrollment e "
        "JOIN Course c ON e.course_id=c.course_id "
        "LEFT JOIN Instructor i ON c.instructor_id=i.instructor_id "
        "WHERE e.student_id=? ORDER BY e.enrolled_at DESC", (sid,)
    )
    graded = [e for e in enrollments if e['grade'] is not None]
    gpa = round(sum(e['grade'] for e in graded) / len(graded), 2) if graded else None
    return render_template('student_grades.html', enrollments=enrollments, gpa=gpa)

@app.route('/student/profile')
@login_required
@role_required('student')
def student_profile():
    sid     = session.get('profile_id')
    student = query("SELECT * FROM Student WHERE student_id=?", (sid,), one=True)
    return render_template('student_profile.html', student=student)

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print("Database not found. Run: python init_db.py")
    app.run(debug=True)
