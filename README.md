# Diabetes Prediction System

A production-quality, responsive web application for predicting diabetes risk using Machine Learning (Logistic Regression), Python Flask, SQLite, and Bootstrap 5.

## Features

1. **User Authentication**: Secure signup and login flow (using hashed passwords via `werkzeug.security`). Supports email or phone number login, automatically calculates user age from Date of Birth, and handles custom profile picture uploads.
2. **Dashboard Analytics**: Shows user profile info, a line graph plotting prediction trend (using Chart.js), quick actions for booking appointments or logging feedback, and a table displaying recent prediction history.
3. **Diabetes Prediction**: Submits medical parameters (Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI, Diabetes Pedigree Function, Age) to the Logistic Regression classifier, maps the probability to a risk level, and stores the results in SQLite.
4. **Doctor Appointment Booking**: Form that schedules appointments with select healthcare professionals and stores bookings.
5. **Feedback System**: Submits complaints, bug reports, or suggestions along with a 1-5 star rating.
6. **Profile Management**: Interface to edit profile details (Full Name, Date of Birth, Gender, Email, Mobile) and upload a new profile photo.

## Technical Stack

- **Backend**: Python, Flask
- **Machine Learning**: Pandas, NumPy, Scikit-learn, Joblib
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons, Chart.js

## Project Directory Layout

```
Diabetes-Prediction-System/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── diabetes.csv
├── database/
│   ├── database.py
│   └── users.db
├── model/
│   ├── train_model.py
│   ├── predict.py
│   ├── diabetes_model.pkl
│   └── scaler.pkl
├── templates/
│   ├── index.html
│   ├── signup.html
│   ├── login.html
│   ├── dashboard.html
│   ├── prediction.html
│   ├── result.html
│   ├── history.html
│   ├── appointment.html
│   ├── feedback.html
│   └── profile.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    ├── images/
    │   ├── logo.png
    │   ├── default_profile.png
    │   ├── diabetes.png
    │   ├── login.png
    │   └── signup.png
    └── uploads/
        └── profile_photos/
```

## Quick Start Setup

### 1. Install Dependencies
Make sure you have Python 3.8+ installed. Open a terminal in the root directory and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Train the Model (Optional)
The model and scaler are pre-trained. If you want to re-train the model on the PIMA dataset:
```bash
python model/train_model.py
```

### 3. Run the Flask Server
Start the development server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000` to access the application.
