import unittest
import os
import sys
import sqlite3

# Ensure project root is in the Python search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
from database.database import get_db_connection

class DiabetesPredictionSystemTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        # Clean up existing test data to ensure a fresh test run
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE email='test_user@example.com' OR mobile='1234509876'")
        conn.commit()
        conn.close()

    def tearDown(self):
        pass

    def test_complete_user_flow(self):
        # 1. Sign Up Route Verification
        signup_data = {
            'fullname': 'John Testing',
            'dob': '1992-06-15',
            'gender': 'Male',
            'email': 'test_user@example.com',
            'mobile': '1234509876',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        
        response = self.client.post('/signup', data=signup_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful", response.data)

        # Retrieve user to verify SQLite database insertion
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email='test_user@example.com'").fetchone()
        conn.close()
        self.assertIsNotNone(user)
        self.assertEqual(user['fullname'], 'John Testing')
        self.assertEqual(user['gender'], 'Male')
        self.assertEqual(user['mobile'], '1234509876')
        
        # Age should be calculated correctly (dob is 1992-06-15, so 34 years in 2026)
        self.assertEqual(user['age'], 34)

        # 2. Login Route Verification
        login_data = {
            'username': 'test_user@example.com',
            'password': 'password123'
        }
        response = self.client.post('/login', data=login_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome back", response.data)
        self.assertIn(b"John Testing", response.data)

        # 3. Prediction Submission and Model Prediction Verification
        predict_data = {
            'pregnancies': '2',
            'glucose': '135',
            'blood_pressure': '80',
            'skin_thickness': '28',
            'insulin': '85',
            'bmi': '29.3',
            'pedigree': '0.450',
            'age': '34'
        }
        response = self.client.post('/predict', data=predict_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Prediction Report", response.data)

        # Verify prediction result is stored in database
        conn = get_db_connection()
        prediction = conn.execute("SELECT * FROM predictions WHERE user_id=?", (user['id'],)).fetchone()
        conn.close()
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction['glucose'], 135)
        self.assertEqual(prediction['bmi'], 29.3)
        self.assertIn(prediction['risk'], ['Low', 'Medium', 'High'])
        self.assertTrue(0 <= prediction['probability'] <= 100)

        # 4. History Screen Verification
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Prediction History", response.data)
        self.assertIn(b"135", response.data) # glucose value
        self.assertIn(b"29.3", response.data) # bmi value

        # 5. Doctor Appointment Booking Verification
        appt_data = {
            'doctor': 'Dr. Sneha Patel',
            'hospital': 'St. Jude Healthcare',
            'date': '2026-07-28',
            'time': '10:00',
            'reason': 'Routine diabetes monitoring consultation'
        }
        response = self.client.post('/appointment', data=appt_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Doctor appointment successfully booked", response.data)

        # Verify appointment stored in database
        conn = get_db_connection()
        appt = conn.execute("SELECT * FROM appointments WHERE user_id=?", (user['id'],)).fetchone()
        conn.close()
        self.assertIsNotNone(appt)
        self.assertEqual(appt['doctor_name'], 'Dr. Sneha Patel')
        self.assertEqual(appt['hospital'], 'St. Jude Healthcare')

        # 6. Feedback Log Verification
        feedback_data = {
            'type': 'Suggestion',
            'rating': '⭐⭐⭐⭐⭐ Excellent',
            'message': 'Highly visual and responsive interface.'
        }
        response = self.client.post('/feedback', data=feedback_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Feedback received successfully", response.data)

        # Verify feedback stored in database
        conn = get_db_connection()
        fb = conn.execute("SELECT * FROM feedback WHERE user_id=?", (user['id'],)).fetchone()
        conn.close()
        self.assertIsNotNone(fb)
        self.assertEqual(fb['feedback_type'], 'Suggestion')
        self.assertEqual(fb['rating'], '5')

        # 7. Edit Profile Verification
        profile_data = {
            'fullname': 'John Updated',
            'dob': '1992-06-15',
            'gender': 'Male',
            'email': 'test_user@example.com',
            'mobile': '1234509877' # updated mobile number
        }
        response = self.client.post('/profile', data=profile_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Profile updated successfully", response.data)

        # Verify profile database values are updated
        conn = get_db_connection()
        updated_user = conn.execute("SELECT * FROM users WHERE id=?", (user['id'],)).fetchone()
        conn.close()
        self.assertEqual(updated_user['fullname'], 'John Updated')
        self.assertEqual(updated_user['mobile'], '1234509877')

        # 8. Logout Verification
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You have been logged out", response.data)

if __name__ == '__main__':
    unittest.main()
