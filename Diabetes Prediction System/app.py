from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
import sqlite3
from datetime import datetime
import joblib
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Import database functions
from database.database import (
    init_db,
    create_user,
    get_user_by_email,
    get_user_by_mobile,
    get_user_by_id,
    update_user,
    save_prediction,
    get_predictions_by_user,
    create_appointment,
    create_feedback
)

app = Flask(__name__)
app.secret_key = 'diabetes_prediction_secret_key_12345'

# File upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profile_photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the database
with app.app_context():
    init_db()

# Load Machine Learning Model and Scaler
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'diabetes_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'model', 'scaler.pkl')

model = None
scaler = None

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    else:
        print("Warning: Model or scaler file not found. Please train the model first.")
except Exception as e:
    print(f"Error loading model or scaler: {e}")

# Helper: calculate age from date of birth string (YYYY-MM-DD)
def calculate_age(dob_str):
    try:
        birth_date = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except Exception:
        return 0

# --- ROUTES ---

@app.route('/')
def home():
    # Set a flag in session to show dashboard or login/signup on index
    user_name = session.get('user_name')
    return render_template('index.html', user_name=user_name)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Basic Validations
        if not (fullname and dob and gender and email and mobile and password and confirm_password):
            flash("All fields are required!", "danger")
            return render_template('signup.html')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template('signup.html')

        # Check unique constraints
        if get_user_by_email(email):
            flash("Email is already registered!", "danger")
            return render_template('signup.html')

        if get_user_by_mobile(mobile):
            flash("Mobile number is already registered!", "danger")
            return render_template('signup.html')

        # Calculate Age
        age = calculate_age(dob)

        # Handle profile photo upload
        profile_photo_filename = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '' and allowed_file(file.filename):
                # Save with clean name prefixed by timestamp to prevent duplicate collisions
                ext = file.filename.rsplit('.', 1)[1].lower()
                clean_filename = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], clean_filename))
                profile_photo_filename = clean_filename

        # Hash password and create user
        password_hash = generate_password_hash(password)
        user_id = create_user(
            fullname=fullname,
            dob=dob,
            age=age,
            gender=gender,
            email=email,
            mobile=mobile,
            password_hash=password_hash,
            profile_photo=profile_photo_filename
        )

        if user_id:
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("An error occurred during registration. Please try again.", "danger")
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Please enter both email/mobile and password.", "danger")
            return render_template('login.html')

        # Check if username is email or mobile
        user = get_user_by_email(username)
        if not user:
            user = get_user_by_mobile(username)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['fullname']
            flash(f"Welcome back, {user['fullname']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email/mobile or password.", "danger")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    predictions = get_predictions_by_user(user['id'])

    # Trend Chart Data: chronological order of predictions (up to last 10)
    chart_predictions = predictions[:10][::-1]
    graph_labels = [datetime.strptime(p['date'], "%Y-%m-%d %H:%M:%S").strftime("%m/%d %H:%M") if len(p['date']) > 10 else p['date'] for p in chart_predictions]
    graph_data = [p['probability'] for p in chart_predictions]

    # Handle cases with no data points
    if not graph_data:
        graph_labels = ["No Predictions"]
        graph_data = [0]

    return render_template(
        'dashboard.html',
        user_name=user['fullname'],
        age=user['age'],
        gender=user['gender'],
        phone=user['mobile'],
        email=user['email'],
        profile_photo=user['profile_photo'],
        history=predictions[:5],  # Recent 5 items for dashboard
        graph_labels=graph_labels,
        graph_data=graph_data
    )

@app.route('/prediction')
def prediction():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))

    return render_template('prediction.html', age=user['age'])

@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Load ML components on demand if not loaded at start
    global model, scaler
    try:
        if not model or not scaler:
            model = joblib.load(MODEL_PATH)
            scaler = joblib.load(SCALER_PATH)
    except Exception as e:
        flash(f"ML Model is not trained or loaded: {e}", "danger")
        return redirect(url_for('prediction'))

    try:
        pregnancies = int(request.form.get('pregnancies', 0))
        glucose = float(request.form.get('glucose', 0))
        blood_pressure = float(request.form.get('blood_pressure', 0))
        skin_thickness = float(request.form.get('skin_thickness', 0))
        insulin = float(request.form.get('insulin', 0))
        bmi = float(request.form.get('bmi', 0))
        pedigree = float(request.form.get('pedigree', 0))
        age = int(request.form.get('age', 0))

        # Check for non-negative bounds
        if pregnancies < 0 or glucose < 0 or blood_pressure < 0 or skin_thickness < 0 or insulin < 0 or bmi < 0 or pedigree < 0 or age < 0:
            flash("All clinical inputs must be non-negative values.", "danger")
            return redirect(url_for('prediction'))

        # Prepare vector for prediction
        input_data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age]])
        input_scaled = scaler.transform(input_data)
        
        pred_class = model.predict(input_scaled)[0]
        prob_diabetic = model.predict_proba(input_scaled)[0][1]
        prob_percentage = round(prob_diabetic * 100, 2)

        prediction_label = "Likely Diabetic" if pred_class == 1 else "Likely Non-Diabetic"

        # Categorize risk
        if prob_percentage >= 75.0:
            risk_level = "High"
        elif prob_percentage >= 50.0:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to SQLite DB
        save_prediction(
            user_id=session['user_id'],
            date=date_str,
            pregnancies=pregnancies,
            glucose=glucose,
            blood_pressure=blood_pressure,
            skin_thickness=skin_thickness,
            insulin=insulin,
            bmi=bmi,
            pedigree=pedigree,
            age=age,
            prediction=prediction_label,
            probability=prob_percentage,
            risk=risk_level
        )

        return redirect(url_for('result'))

    except ValueError:
        flash("Invalid numerical values submitted. Please re-check forms.", "danger")
        return redirect(url_for('prediction'))
    except Exception as e:
        flash(f"An unexpected error occurred: {e}", "danger")
        return redirect(url_for('prediction'))

@app.route('/result')
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch latest prediction for this user
    predictions = get_predictions_by_user(session['user_id'])
    if not predictions:
        flash("No predictions found. Let's make one first!", "info")
        return redirect(url_for('prediction'))

    latest = predictions[0]

    return render_template(
        'result.html',
        prediction=latest['prediction'],
        probability=latest['probability'],
        risk=latest['risk']
    )

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    predictions = get_predictions_by_user(session['user_id'])
    return render_template('history.html', history=predictions)

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_name = request.form.get('doctor')
        hospital = request.form.get('hospital')
        date = request.form.get('date')
        time = request.form.get('time')
        reason = request.form.get('reason')

        if not (doctor_name and hospital and date and time and reason):
            flash("All fields must be filled out to book an appointment.", "danger")
            return render_template('appointment.html', user_name=user['fullname'])

        create_appointment(
            user_id=session['user_id'],
            doctor_name=doctor_name,
            hospital=hospital,
            appointment_date=date,
            appointment_time=time,
            reason=reason,
            status='Booked'
        )

        flash("Doctor appointment successfully booked!", "success")
        return redirect(url_for('dashboard'))

    return render_template('appointment.html', user_name=user['fullname'])

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        feedback_type = request.form.get('type')
        rating_raw = request.form.get('rating')
        message = request.form.get('message')

        if not (feedback_type and rating_raw and message):
            flash("Please fill in feedback type, rating, and message fields.", "danger")
            return render_template('feedback.html', user_name=user['fullname'], email=user['email'])

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Strip stars for database rating
        rating = rating_raw.split(" ")[0].replace("⭐", "")
        if not rating.isdigit():
            rating = "5" # fallback to 5 star equivalent

        create_feedback(
            user_id=session['user_id'],
            feedback_type=feedback_type,
            rating=rating,
            message=message,
            created_at=created_at
        )

        flash("Thank you! Feedback received successfully.", "success")
        return redirect(url_for('dashboard'))

    return render_template('feedback.html', user_name=user['fullname'], email=user['email'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        email = request.form.get('email')
        mobile = request.form.get('mobile')

        if not (fullname and dob and gender and email and mobile):
            flash("All fields are required to update your profile.", "danger")
            return render_template('profile.html', user=user)

        # Check unique constraints if changed
        if email != user['email']:
            other_email = get_user_by_email(email)
            if other_email:
                flash("Email address is already in use by another account.", "danger")
                return render_template('profile.html', user=user)

        if mobile != user['mobile']:
            other_mobile = get_user_by_mobile(mobile)
            if other_mobile:
                flash("Mobile number is already in use by another account.", "danger")
                return render_template('profile.html', user=user)

        # Calculate Age
        age = calculate_age(dob)

        # Profile image upload
        profile_photo_filename = user['profile_photo']
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                clean_filename = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], clean_filename))
                
                # Delete old photo if it exists and isn't the default
                if user['profile_photo'] and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], user['profile_photo'])):
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user['profile_photo']))
                    except Exception:
                        pass # Ignore deletions issues
                        
                profile_photo_filename = clean_filename

        success = update_user(
            user_id=user['id'],
            fullname=fullname,
            dob=dob,
            age=age,
            gender=gender,
            email=email,
            mobile=mobile,
            profile_photo=profile_photo_filename
        )

        if success:
            session['user_name'] = fullname
            flash("Profile updated successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("An error occurred. Please try again.", "danger")
            return render_template('profile.html', user=user)

    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
