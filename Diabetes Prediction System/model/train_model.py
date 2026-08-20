#Libraries
import pandas as rd #To read Dataset
import joblib # Dumping model the data into packages
import matplotlib.pyplot as plt #Graphs
import seaborn as sns #Heatmap

from sklearn.model_selection import train_test_split #Split data for train and testing
from sklearn.preprocessing import StandardScaler #feature Scaling
from sklearn.linear_model import LogisticRegression #Model:- LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)

import os

csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "diabetes.csv")
df = rd.read_csv(csv_path) #load dataset

columns = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI"
] #columns that are need not to be Zero

for column in columns:
    df[column] = df[column].replace(0, df[column].median()) #replace with median

X = df.drop("Outcome", axis=1) #Features
y = df["Outcome"] #target Outcomes

#Feature Scaling
scalar = StandardScaler()
x_scaled = scalar.fit_transform(X) # Making features into closed Ranges

#training and test
X_train,X_test,y_train,y_test = train_test_split(
    x_scaled,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = LogisticRegression(max_iter=1000) #Model Creation

model.fit(X_train,y_train) #Training Model

y_pred = model.predict(X_test)

y_prob = model.predict_proba(X_test)[:,1]

#Evalution of Model
accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy :", round(accuracy*100,2),"%")

print("\nConfusion Matrix")
cm = confusion_matrix(y_test,y_pred)
print(cm)

print("\nClassification Report")
print(classification_report(y_test,y_pred))

print("ROC AUC :",roc_auc_score(y_test,y_prob))

#Training Accuracy
train_accuracy = model.score(X_train,y_train)
print("\nTraining Accuracy :",round(train_accuracy*100,2),"%")

#Validation Accuracy
validation_accuracy = model.score(X_test,y_test)
print("Validation Accuracy :",round(validation_accuracy*100,2),"%")

# Feature Importance
importance = rd.DataFrame({
    "Feature":X.columns,
    "Coefficient":model.coef_[0]
})

importance["Absolute"] = importance["Coefficient"].abs()

importance = importance.sort_values(
    by="Absolute",
    ascending=False
)

print("\nFeature Importance")
print(importance)

model_path = os.path.join(os.path.dirname(__file__), "diabetes_model.pkl")
scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")

joblib.dump(model, model_path)
joblib.dump(scalar, scaler_path)

print("\nModel Saved Successfully!")

