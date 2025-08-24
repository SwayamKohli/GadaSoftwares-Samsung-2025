import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../model/model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "../model/scaler.pkl")

# Load model and scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

def predict(features: list):
    """
    Runs inference on input features.
    """
    # Ensure features are scaled
    scaled_features = scaler.transform([features])
    prediction = model.predict(scaled_features)
    return prediction[0]
