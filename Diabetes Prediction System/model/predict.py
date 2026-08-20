#Diabeties Prediction System
#libraries
import joblib
import numpy as np
#Model Loading
model = joblib.load("diabetes_model.pkl")
scalar = joblib.load("scaler.pkl")
#Taking Input Features
pregnancies = int(input("Pregnancies : "))
glucose = float(input("Glucose : "))
blood_pressure = float(input("Blood Pressure : "))
skin_thickness = float(input("Skin Thickness : "))
insulin = float(input("Insulin : "))
bmi = float(input("BMI : "))
pedigree = float(input("Diabetes Pedigree Function : "))
age = int(input("Age : "))
#input Array
input_data = np.array([[pregnancies,
    glucose,
    blood_pressure,
    skin_thickness,
    insulin,
    bmi,
    pedigree,
    age]])
input_scaled = scalar.transform(input_data)
prediction = model.predict(input_scaled)
probability = model.predict_proba(input_scaled)
#Output
if prediction[0] == 1:
    print("Prediction : Likely Diabetic")
else:
    print("Prediction : Likely Non-Diabetic")
print()
print("Probability")
print("Non-Diabetic : {:.2f}%".format(probability[0][0]*100))
print("Diabetic     : {:.2f}%".format(probability[0][1]*100))
