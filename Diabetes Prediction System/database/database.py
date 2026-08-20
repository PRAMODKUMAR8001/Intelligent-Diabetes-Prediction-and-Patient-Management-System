import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            dob TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            profile_photo TEXT
        )
    ''')

    # Create predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            pregnancies INTEGER NOT NULL,
            glucose REAL NOT NULL,
            blood_pressure REAL NOT NULL,
            skin_thickness REAL NOT NULL,
            insulin REAL NOT NULL,
            bmi REAL NOT NULL,
            pedigree REAL NOT NULL,
            age INTEGER NOT NULL,
            prediction TEXT NOT NULL,
            probability REAL NOT NULL,
            risk TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doctor_name TEXT NOT NULL,
            hospital TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Booked',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            rating TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# --- User Database Helper Functions ---

def create_user(fullname, dob, age, gender, email, mobile, password_hash, profile_photo=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (fullname, dob, age, gender, email, mobile, password_hash, profile_photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (fullname, dob, age, gender, email, mobile, password_hash, profile_photo))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError as e:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_by_mobile(mobile):
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE mobile = ?', (mobile,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def update_user(user_id, fullname, dob, age, gender, email, mobile, profile_photo):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE users
            SET fullname = ?, dob = ?, age = ?, gender = ?, email = ?, mobile = ?, profile_photo = ?
            WHERE id = ?
        ''', (fullname, dob, age, gender, email, mobile, profile_photo, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# --- Prediction Helper Functions ---

def save_prediction(user_id, date, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age, prediction, probability, risk):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (user_id, date, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age, prediction, probability, risk)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, date, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age, prediction, probability, risk))
    conn.commit()
    conn.close()

def get_predictions_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute('''
        SELECT * FROM predictions WHERE user_id = ? ORDER BY id DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return rows

# --- Appointment Helper Functions ---

def create_appointment(user_id, doctor_name, hospital, appointment_date, appointment_time, reason, status='Booked'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (user_id, doctor_name, hospital, appointment_date, appointment_time, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, doctor_name, hospital, appointment_date, appointment_time, reason, status))
    conn.commit()
    conn.close()

def get_appointments_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute('''
        SELECT * FROM appointments WHERE user_id = ? ORDER BY id DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return rows

# --- Feedback Helper Functions ---

def create_feedback(user_id, feedback_type, rating, message, created_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (user_id, feedback_type, rating, message, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, feedback_type, rating, message, created_at))
    conn.commit()
    conn.close()
