import joblib
import pandas as pd


MODEL_FILE = "ml/priority_model.pkl"
ENCODER_FILE = "ml/priority_encoder.pkl"


# Load trained model
model = joblib.load(MODEL_FILE)

# Load encoders
encoders = joblib.load(ENCODER_FILE)

category_encoder = encoders["category_encoder"]
location_encoder = encoders["location_encoder"]


def predict_priority(
    category,
    location,
    severity,
    urgency
):

    # Validate category
    if category not in category_encoder.classes_:
        category = category_encoder.classes_[0]

    # Validate location
    if location not in location_encoder.classes_:
        location = location_encoder.classes_[0]

    category_encoded = category_encoder.transform(
        [category]
    )[0]

    location_encoded = location_encoder.transform(
        [location]
    )[0]

    data = pd.DataFrame(
        [[
            category_encoded,
            location_encoded,
            severity,
            urgency
        ]],
        columns=[
            "Category_Encoded",
            "Location_Encoded",
            "Severity",
            "Urgency"
        ]
    )

    prediction = model.predict(data)[0]

    return prediction