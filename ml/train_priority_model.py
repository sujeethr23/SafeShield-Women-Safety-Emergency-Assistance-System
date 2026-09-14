import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


# ==========================================
# SAFESHIELD AI PRIORITY MODEL TRAINING
# ==========================================

DATA_FILE = "ml/priority_training_data.csv"
MODEL_FILE = "ml/priority_model.pkl"
ENCODER_FILE = "ml/priority_encoder.pkl"


print("=" * 50)
print("SAFESHIELD AI PRIORITY MODEL TRAINING")
print("=" * 50)


# ==========================================
# 1. LOAD DATASET
# ==========================================

df = pd.read_csv(DATA_FILE)

print(f"\nTotal records: {len(df)}")

print("\nDataset columns:")
print(list(df.columns))


# ==========================================
# 2. ENCODE TEXT FEATURES
# ==========================================

category_encoder = LabelEncoder()
location_encoder = LabelEncoder()

df["Category_Encoded"] = category_encoder.fit_transform(
    df["Category"]
)

df["Location_Encoded"] = location_encoder.fit_transform(
    df["Location"]
)


# ==========================================
# 3. FEATURES AND TARGET
# ==========================================

X = df[
    [
        "Category_Encoded",
        "Location_Encoded",
        "Severity",
        "Urgency"
    ]
]

y = df["Priority"]


# ==========================================
# 4. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print(f"\nTraining records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")


# ==========================================
# 5. CREATE MODEL
# ==========================================

model = DecisionTreeClassifier(
    max_depth=6,
    random_state=42
)


# ==========================================
# 6. TRAIN MODEL
# ==========================================

print("\nTraining model...")

model.fit(X_train, y_train)


# ==========================================
# 7. TEST MODEL
# ==========================================

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)


print("\n==========================================")
print("MODEL RESULTS")
print("==========================================")

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# ==========================================
# 8. SAVE MODEL
# ==========================================

joblib.dump(
    model,
    MODEL_FILE
)


# Save both encoders
joblib.dump(
    {
        "category_encoder": category_encoder,
        "location_encoder": location_encoder
    },
    ENCODER_FILE
)


print("\n==========================================")
print("MODEL SAVED SUCCESSFULLY")
print("==========================================")

print(f"\nModel: {MODEL_FILE}")
print(f"Encoders: {ENCODER_FILE}")


# ==========================================
# 9. TEST SAMPLE PREDICTION
# ==========================================

sample_category = "Threat"
sample_location = "Road"
sample_severity = 5
sample_urgency = 5


category_value = category_encoder.transform(
    [sample_category]
)[0]

location_value = location_encoder.transform(
    [sample_location]
)[0]


sample = [[
    category_value,
    location_value,
    sample_severity,
    sample_urgency
]]


sample_prediction = model.predict(sample)[0]


print("\n==========================================")
print("TEST PREDICTION")
print("==========================================")

print(f"Category : {sample_category}")
print(f"Location : {sample_location}")
print(f"Severity : {sample_severity}")
print(f"Urgency  : {sample_urgency}")

print(f"\nAI Predicted Priority: {sample_prediction}")

print("\nTraining completed successfully.")