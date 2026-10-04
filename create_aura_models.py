# ============================================================
# AURA AI - ONE CLICK MODEL TRAINING SCRIPT
# Generates:
#   models/productivity_model.pkl
#   models/burnout_model.pkl
# ============================================================

import os
import sys
import subprocess

# ------------------------------------------------------------
# 1. INSTALL REQUIRED LIBRARIES IF MISSING
# ------------------------------------------------------------

required_packages = {
    "numpy": "numpy",
    "pandas": "pandas",
    "sklearn": "scikit-learn",
    "joblib": "joblib",
}

for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package]
        )


# ------------------------------------------------------------
# 2. IMPORT LIBRARIES
# ------------------------------------------------------------

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ------------------------------------------------------------
# 3. PROJECT PATHS
# ------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(SCRIPT_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)


# ------------------------------------------------------------
# 4. AURA FEATURES
# MUST MATCH app.py EXACTLY
# ------------------------------------------------------------

FEATURE_NAMES = [
    "Sleep_Hours",
    "Stress_Level",
    "Screen_Time",
    "Workload",
    "Break_Frequency",
    "Mood_Score",
    "Physical_Activity",
    "Water_Intake",
    "Study_Hours",
    "Focus_Sessions",
    "Social_Media_Time",
    "Deadline_Pressure",
    "Heart_Rate",
    "Energy_Level",
    "Task_Completion_Rate",
]


# ------------------------------------------------------------
# 5. GENERATE SYNTHETIC TRAINING DATA
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("        AURA AI MODEL TRAINING")
print("=" * 65)

print("\nGenerating 10,000 training samples...")

np.random.seed(42)

N = 10000

data = pd.DataFrame({
    "Sleep_Hours":
        np.clip(np.random.normal(7, 1.2, N), 4, 10),

    "Stress_Level":
        np.random.randint(1, 11, N),

    "Screen_Time":
        np.clip(np.random.normal(6, 2, N), 1, 12),

    "Workload":
        np.random.randint(1, 11, N),

    "Break_Frequency":
        np.random.randint(1, 11, N),

    "Mood_Score":
        np.random.randint(1, 11, N),

    "Physical_Activity":
        np.random.randint(1, 11, N),

    "Water_Intake":
        np.random.randint(1, 11, N),

    "Study_Hours":
        np.clip(np.random.normal(5, 2, N), 0, 12),

    "Focus_Sessions":
        np.random.randint(1, 11, N),

    "Social_Media_Time":
        np.clip(np.random.normal(3, 2, N), 0, 10),

    "Deadline_Pressure":
        np.random.randint(1, 11, N),

    "Heart_Rate":
        np.clip(np.random.normal(75, 12, N), 50, 120),

    "Energy_Level":
        np.random.randint(1, 11, N),

    "Task_Completion_Rate":
        np.random.randint(20, 101, N),
})


# ------------------------------------------------------------
# 6. CREATE LATENT PRODUCTIVITY SCORE
# ------------------------------------------------------------

productivity_score = (
    data["Sleep_Hours"] * 7
    + data["Mood_Score"] * 5
    + data["Physical_Activity"] * 3
    + data["Water_Intake"] * 2
    + data["Study_Hours"] * 4
    + data["Focus_Sessions"] * 5
    + data["Energy_Level"] * 5
    + data["Task_Completion_Rate"] * 0.35
    + data["Break_Frequency"] * 2

    - data["Stress_Level"] * 4
    - data["Screen_Time"] * 2
    - data["Workload"] * 2
    - data["Social_Media_Time"] * 2
    - data["Deadline_Pressure"] * 3
)


# ------------------------------------------------------------
# 7. CREATE LATENT BURNOUT SCORE
# Higher = MORE burnout
# ------------------------------------------------------------

burnout_score = (
    data["Stress_Level"] * 7
    + data["Workload"] * 5
    + data["Screen_Time"] * 3
    + data["Social_Media_Time"] * 2
    + data["Deadline_Pressure"] * 6
    + data["Heart_Rate"] * 0.25

    - data["Sleep_Hours"] * 6
    - data["Mood_Score"] * 4
    - data["Physical_Activity"] * 3
    - data["Water_Intake"] * 2
    - data["Energy_Level"] * 4
    - data["Break_Frequency"] * 2
    - data["Task_Completion_Rate"] * 0.20
)


# ------------------------------------------------------------
# 8. NORMALIZE SCORES
# ------------------------------------------------------------

def normalize(series):

    minimum = series.min()
    maximum = series.max()

    return (
        (series - minimum)
        / (maximum - minimum)
        * 100
    )


productivity_score = normalize(productivity_score)

burnout_score = normalize(burnout_score)


# ------------------------------------------------------------
# 9. ADD SMALL RANDOM VARIATION
# ------------------------------------------------------------

productivity_score += np.random.normal(0, 4, N)
burnout_score += np.random.normal(0, 4, N)

productivity_score = np.clip(
    productivity_score,
    0,
    100
)

burnout_score = np.clip(
    burnout_score,
    0,
    100
)


# ------------------------------------------------------------
# 10. CREATE PRODUCTIVITY LABELS
# ------------------------------------------------------------

data["Productivity"] = np.select(
    [
        productivity_score >= 67,
        productivity_score >= 40
    ],
    [
        "High",
        "Medium"
    ],
    default="Low"
)


# ------------------------------------------------------------
# 11. CREATE BURNOUT LABELS
# ------------------------------------------------------------

data["Burnout"] = np.select(
    [
        burnout_score < 35,
        burnout_score < 65
    ],
    [
        "Safe",
        "Warning"
    ],
    default="Critical"
)


# ------------------------------------------------------------
# 12. FEATURES + TARGETS
# ------------------------------------------------------------

X = data[FEATURE_NAMES]

y_productivity = data["Productivity"]

y_burnout = data["Burnout"]


# ------------------------------------------------------------
# 13. TRAIN / TEST SPLIT
# ------------------------------------------------------------

X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(
    X,
    y_productivity,
    test_size=0.20,
    random_state=42,
    stratify=y_productivity
)

X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
    X,
    y_burnout,
    test_size=0.20,
    random_state=42,
    stratify=y_burnout
)


# ------------------------------------------------------------
# 14. TRAIN PRODUCTIVITY MODEL
# ------------------------------------------------------------

print("\nTraining Productivity Model...")

productivity_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

productivity_model.fit(
    X_train_p,
    y_train_p
)


# ------------------------------------------------------------
# 15. TRAIN BURNOUT MODEL
# ------------------------------------------------------------

print("Training Burnout Model...")

burnout_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

burnout_model.fit(
    X_train_b,
    y_train_b
)


# ------------------------------------------------------------
# 16. TEST MODELS
# ------------------------------------------------------------

productivity_predictions = productivity_model.predict(X_test_p)

burnout_predictions = burnout_model.predict(X_test_b)

productivity_accuracy = accuracy_score(
    y_test_p,
    productivity_predictions
)

burnout_accuracy = accuracy_score(
    y_test_b,
    burnout_predictions
)


# ------------------------------------------------------------
# 17. SAVE MODELS
# ------------------------------------------------------------

productivity_path = os.path.join(
    MODEL_DIR,
    "productivity_model.pkl"
)

burnout_path = os.path.join(
    MODEL_DIR,
    "burnout_model.pkl"
)

joblib.dump(
    productivity_model,
    productivity_path
)

joblib.dump(
    burnout_model,
    burnout_path
)


# ------------------------------------------------------------
# 18. VERIFY SAVED MODELS
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("                 TRAINING COMPLETE")
print("=" * 65)

print("\nModel Results:")
print(
    f"Productivity Accuracy : "
    f"{productivity_accuracy * 100:.2f}%"
)

print(
    f"Burnout Accuracy      : "
    f"{burnout_accuracy * 100:.2f}%"
)

print("\nClasses:")

print(
    "Productivity:",
    list(productivity_model.classes_)
)

print(
    "Burnout:",
    list(burnout_model.classes_)
)

print("\nSaved files:")

print(productivity_path)
print(burnout_path)


# ------------------------------------------------------------
# 19. VERIFY THAT FILES EXIST
# ------------------------------------------------------------

if os.path.exists(productivity_path):
    print("\n✅ productivity_model.pkl created successfully.")

else:
    print("\n❌ Productivity model was NOT created.")


if os.path.exists(burnout_path):
    print("✅ burnout_model.pkl created successfully.")

else:
    print("❌ Burnout model was NOT created.")


# ------------------------------------------------------------
# 20. TEST WITH A SAMPLE USER
# ------------------------------------------------------------

sample_user = pd.DataFrame([{
    "Sleep_Hours": 7,
    "Stress_Level": 5,
    "Screen_Time": 6,
    "Workload": 5,
    "Break_Frequency": 5,
    "Mood_Score": 5,
    "Physical_Activity": 1,
    "Water_Intake": 2,
    "Study_Hours": 5,
    "Focus_Sessions": 5,
    "Social_Media_Time": 5,
    "Deadline_Pressure": 2,
    "Heart_Rate": 75,
    "Energy_Level": 5,
    "Task_Completion_Rate": 70,
}])

sample_productivity = productivity_model.predict(
    sample_user
)[0]

sample_burnout = burnout_model.predict(
    sample_user
)[0]

print("\n" + "-" * 65)
print("Sample AURA Prediction")
print("-" * 65)

print(
    "Productivity :",
    sample_productivity
)

print(
    "Burnout      :",
    sample_burnout
)

print("-" * 65)

print("\n🎉 AURA models are ready to use!")
print("\nYou can now run your Streamlit application.")
print("=" * 65)

input("\nPress ENTER to close...")