"""
Training a Random Forest model to classify traffic as Real-Time vs Non-Real-Time.
Saves: model.pkl, scaler.pkl, label_encoder.pkl
"""

import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import os

# -------------------------------
# Configuration
# -------------------------------
DATASET_PATH = '../data/Samsung_dataset.csv'  
MODEL_DIR = '.'  

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# -------------------------------
# Load and Prepare Data
# -------------------------------
print("Loading dataset...")
df = pd.read_csv(DATASET_PATH)

# Convert Timestamp to numeric
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Timestamp_Formatted'] = df['Timestamp'].apply(lambda x: x.timestamp())

# Define features and target
features = [
    'Source.Port', 'Destination.Port', 'Flow.Duration',
    'Total.Fwd.Packets', 'Total.Backward.Packets',
    'Flow.Packets.s', 'Fwd.Packet.Length.Max', 'Flow.IAT.Max',
    'Bwd.Packet.Length.Max', 'Init_Win_bytes_forward',
    'Init_Win_bytes_backward', 'Timestamp_Formatted'
]
target = 'ProtocolCategory'

X = df[features]
y = df[target]

# Encode labels: 'real-time' / 'non-real-time' → 0 / 1
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Verify classes
print("Classes found:", list(le.classes_))
if len(le.classes_) != 2:
    raise ValueError("Target must have exactly two classes: 'real-time' and 'non-real-time'")

# -------------------------------
# Train-Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded  # Keep class balance
)

# -------------------------------
# Feature Scaling
# -------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------------------
# Train Model
# -------------------------------
print("Training Random Forest model...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# -------------------------------
# Evaluate Model
# -------------------------------
y_pred = rf_model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, target_names=le.classes_)

print("\nModel Accuracy:", accuracy)
print("Classification Report:")
print(report)

# -------------------------------
# Save Artifacts
# -------------------------------
model_path = os.path.join(MODEL_DIR, 'model.pkl')
scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
encoder_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')

with open(model_path, 'wb') as f:
    pickle.dump(rf_model, f)
print("Model saved to", model_path)

with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print("Scaler saved to", scaler_path)

with open(encoder_path, 'wb') as f:
    pickle.dump(le, f)
print("Label encoder saved to", encoder_path)

print("\nTraining complete.")