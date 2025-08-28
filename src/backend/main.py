import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

import numpy as np
import pickle
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from joblib import load
import sys

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "model"
DATA_DIR = ROOT / "data"

sys.path.append(str(DATA_DIR))

LABEL_ENCODER_PATH = MODEL_DIR / "multi_label_encoder.pkl"
label_encoder = None

if LABEL_ENCODER_PATH.exists():
    try:
        with open(LABEL_ENCODER_PATH, 'rb') as f:
            label_encoder = pickle.load(f)
        print(f"✅ Label encoder loaded from {LABEL_ENCODER_PATH}")
        print("Label mapping:")
        for i, cls in enumerate(label_encoder.classes_):
            print(f"  {i} → {cls}")
    except Exception as e:
        print(f"❌ Failed to load label_encoder.pkl: {e}")
else:
    print(f"⚠️ multi_label_encoder.pkl not found at {LABEL_ENCODER_PATH}")

try:
    from synthetic_flows import generate_flows
    print("✅ synthetic_flows.py loaded successfully")
except Exception as e:
    print(f"❌ Failed to load synthetic_flows.py: {e}")
    generate_flows = None

WEBSITE_TEST_PATH = DATA_DIR / "website_testing.csv"
website_test_data = []

if WEBSITE_TEST_PATH.exists():
    try:
        import pandas as pd
        df = pd.read_csv(WEBSITE_TEST_PATH)
        feature_cols = [
            'Flow.Duration',
            'Total.Fwd.Packets', 'Total.Backward.Packets',
            'Flow.Packets.s', 'Fwd.Packet.Length.Max', 'Flow.IAT.Max',
            'Bwd.Packet.Length.Max', 'Init_Win_bytes_forward', 'Init_Win_bytes_backward'
        ]
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Missing columns in website_testing.csv: {missing_cols}")
        else:
            for _, row in df.iterrows():
                features = {col: float(row[col]) for col in feature_cols}
                website_test_data.append({"features": features})
            print(f"✅ Loaded {len(website_test_data)} test samples from {WEBSITE_TEST_PATH}")
    except Exception as e:
        print(f"❌ Failed to load website_testing.csv: {e}")
else:
    print(f"⚠️ website_testing.csv not found at {WEBSITE_TEST_PATH}")

app = FastAPI(
    title="Traffic Classifier Backend",
    description="AI backend for multi-class traffic classification: Web, Video, Gaming, etc.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        os.getenv("FRONTEND_ORIGIN", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
log = logging.getLogger("backend")

class PredictIn(BaseModel):
    features: Dict[str, float] = Field(..., description="Feature name to numeric value.")

class PredictOut(BaseModel):
    klass: str = Field(..., description='Predicted class: e.g., "Gaming", "Web", "Video"')
    confidence: Optional[float] = Field(None, ge=0, le=1)

class TestOut(BaseModel):
    count: int
    source: str
    predictions: List[Dict[str, Any]]

class QoSOut(BaseModel):
    klass: str
    qos: Dict[str, str]

class ModelServer:
    def __init__(self, model_dir: Path):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self._load(model_dir)

    def _load(self, model_dir: Path):
        model_path = model_dir / "multi_model.pkl"
        scaler_path = model_dir / "multi_scaler.pkl"

        if model_path.exists():
            try:
                self.model = load(model_path)
                log.info(f"Loaded multi-class model from {model_path}")
            except Exception as e:
                log.exception("Failed to load multi_model.pkl")
                self.model = None
        else:
            log.warning("multi_model.pkl not found")

        if scaler_path.exists():
            try:
                self.scaler = load(scaler_path)
                log.info(f"Loaded scaler from {scaler_path}")
            except Exception:
                log.exception("Failed to load multi_scaler.pkl")
                self.scaler = None
        else:
            log.warning("multi_scaler.pkl not found")

        if self.scaler is not None and hasattr(self.scaler, "feature_names_in_"):
            self.feature_names = list(self.scaler.feature_names_in_)
        elif self.model is not None and hasattr(self.model, "feature_names_in_"):
            self.feature_names = list(self.model.feature_names_in_)
        else:
            self.feature_names = [
                'Flow.Duration',
                'Total.Fwd.Packets', 'Total.Backward.Packets',
                'Flow.Packets.s', 'Fwd.Packet.Length.Max', 'Flow.IAT.Max',
                'Bwd.Packet.Length.Max', 'Init_Win_bytes_forward', 'Init_Win_bytes_backward'
            ]

    def _vectorize(self, features: Dict[str, float]) -> np.ndarray:
        row = [float(features.get(f, 0.0)) for f in self.feature_names]
        X = np.array([row], dtype=float)
        if self.scaler is not None:
            try:
                X = self.scaler.transform(X)
            except Exception as e:
                log.error(f"Scaler.transform failed: {e}")
        return X

    def predict(self, features: Dict[str, float]) -> (str, Optional[float]):
        if self.model is None:
            raise RuntimeError("Model not loaded.")
        X = self._vectorize(features)
        try:
            y = self.model.predict(X)
            raw_label = int(y[0])
        except Exception as e:
            log.exception("Model.predict failed.")
            raise
        if label_encoder is not None:
            try:
                label = label_encoder.inverse_transform([raw_label])[0]
            except Exception:
                log.warning("Label decoding failed; using raw label.")
                label = str(raw_label)
        else:
            label = str(raw_label)
        conf = None
        if hasattr(self.model, "predict_proba"):
            try:
                proba = self.model.predict_proba(X)
                conf = float(np.max(proba[0]))
            except Exception:
                log.warning("predict_proba failed.")
        return str(label), conf

model_server = ModelServer(MODEL_DIR)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_server.model is not None}

@app.post("/predict", response_model=PredictOut)
def predict(req: PredictIn):
    try:
        label, conf = model_server.predict(req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference failed: {str(e)}")
    return PredictOut(klass=label, confidence=conf)

@app.get("/test-synthetic", response_model=TestOut)
def test_synthetic(count: int = Query(10, ge=1, le=100)):
    if generate_flows is None:
        raise HTTPException(status_code=500, detail="Synthetic flow generator not available.")
    try:
        raw_flows = generate_flows(n=count)
        predictions = []
        for item in raw_flows:
            features = item["features"]
            filtered_features = {k: v for k, v in features.items() if k in model_server.feature_names}
            try:
                pred_label, conf = model_server.predict(filtered_features)
                predictions.append({
                    "features": filtered_features,
                    "true_label": item.get("label", "unknown"),
                    "predicted": pred_label,
                    "confidence": conf
                })
            except Exception as e:
                predictions.append({
                    "features": filtered_features,
                    "error": str(e)
                })
        return TestOut(count=len(predictions), source="synthetic", predictions=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate synthetic  {str(e)}")

@app.get("/test-website", response_model=TestOut)
def test_website(limit: int = Query(100, ge=1, le=1000)):
    if not website_test_data:
        raise HTTPException(status_code=404, detail="No website test data available.")
    import random
    sampled_data = random.sample(website_test_data, min(limit, len(website_test_data)))
    predictions = []
    for item in sampled_data:
        features = item["features"]
        try:
            pred_label, conf = model_server.predict(features)
            predictions.append({
                "features": features,
                "predicted": pred_label,
                "confidence": conf
            })
        except Exception as e:
            predictions.append({
                "features": features,
                "error": str(e)
            })
    return TestOut(count=len(predictions), source="website_testing.csv", predictions=predictions)

from qos_engine import get_qos_for_label

@app.get("/qos", response_model=QoSOut)
def qos(class_label: str = Query("Gaming")):
    try:
        policy = get_qos_for_label(class_label)
        return QoSOut(klass=class_label, qos=policy)
    except Exception as e:
        print("QoS error:", e)
        raise HTTPException(status_code=400, detail="Invalid class_label")