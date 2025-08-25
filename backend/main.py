import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

import numpy as np
import pickle
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from joblib import load

# -------------------------
# Paths & Setup
# -------------------------
ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "model"
DATA_DIR = ROOT / "data"

# Add data directory to path to allow import
sys.path.append(str(DATA_DIR))

# Load label encoder
LABEL_ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"
label_encoder = None

if LABEL_ENCODER_PATH.exists():
    try:
        with open(LABEL_ENCODER_PATH, 'rb') as f:
            label_encoder = pickle.load(f)
        print("Label encoder loaded from", LABEL_ENCODER_PATH)
        print("Label mapping:")
        for i, cls in enumerate(label_encoder.classes_):
            print(i, "->", cls)
    except Exception as e:
        print("Failed to load label_encoder.pkl:", e)
else:
    print("label_encoder.pkl not found at", LABEL_ENCODER_PATH)

# Try to import synthetic_flows
try:
    from synthetic_flows import generate_flows
    print("synthetic_flows.py loaded successfully")
except Exception as e:
    print("Failed to load synthetic_flows.py:", e)
    generate_flows = None

# -------------------------
# App & CORS
# -------------------------
app = FastAPI(
    title="Traffic Classifier Backend",
    description="AI backend for Real-Time vs Non-Real-Time traffic classification.",
    version="1.0.0",
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

# -------------------------
# Logging
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
log = logging.getLogger("backend")

# -------------------------
# Pydantic Schemas
# -------------------------
class PredictIn(BaseModel):
    features: Dict[str, float] = Field(..., description="Feature name to numeric value.")

class PredictOut(BaseModel):
    klass: str = Field(..., description='Predicted class: "Real-Time" or "Non-Real-Time"')
    confidence: Optional[float] = Field(None, ge=0, le=1)

class QoSOut(BaseModel):
    klass: str
    qos: Dict[str, Any]

class SimulateOut(BaseModel):
    count: int
    with_predictions: bool
    data: List[Dict[str, Any]]

# -------------------------
# Model Server
# -------------------------
class ModelServer:
    def __init__(self, model_dir: Path):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self._load(model_dir)

    def _load(self, model_dir: Path):
        model_path = model_dir / "model.pkl"
        scaler_path = model_dir / "scaler.pkl"

        # Load model
        if model_path.exists():
            try:
                self.model = load(model_path)
                log.info("Loaded model from %s", model_path)
            except Exception:
                log.exception("Failed to load model.pkl")
                self.model = None
        else:
            log.warning("model.pkl not found")

        # Load scaler
        if scaler_path.exists():
            try:
                self.scaler = load(scaler_path)
                log.info("Loaded scaler from %s", scaler_path)
            except Exception:
                log.exception("Failed to load scaler.pkl")
                self.scaler = None
        else:
            log.warning("scaler.pkl not found")

        # Infer feature order
        if self.scaler is not None and hasattr(self.scaler, "feature_names_in_"):
            self.feature_names = list(self.scaler.feature_names_in_)
        elif self.model is not None and hasattr(self.model, "feature_names_in_"):
            self.feature_names = list(self.model.feature_names_in_)
        else:
            self.feature_names = None

    def _vectorize(self, features: Dict[str, float]) -> np.ndarray:
        if self.feature_names is None:
            self.feature_names = sorted(features.keys())

        row = [float(features.get(f, 0.0)) for f in self.feature_names]
        X = np.array([row], dtype=float)

        if self.scaler is not None:
            try:
                X = self.scaler.transform(X)
            except Exception as e:
                log.error("Scaler.transform failed: %s", e)
        return X

    def predict(self, features: Dict[str, float]) -> (str, Optional[float]):
        if self.model is None:
            raise RuntimeError("Model not loaded.")

        X = self._vectorize(features)

        # Predict label
        try:
            y = self.model.predict(X)
            raw_label = int(y[0])
        except Exception:
            log.exception("Model.predict failed.")
            raise

        # Decode label
        if label_encoder is not None:
            try:
                label = label_encoder.inverse_transform([raw_label])[0]
            except Exception:
                log.warning("Label decoding failed; using raw label.")
                label = str(raw_label)
        else:
            label = str(raw_label)

        # Confidence
        conf = None
        if hasattr(self.model, "predict_proba"):
            try:
                proba = self.model.predict_proba(X)
                classes = getattr(self.model, "classes_", np.array(["Non-Real-Time", "Real-Time"]))
                if "Real-Time" in classes:
                    rt_idx = int(np.where(classes == "Real-Time")[0][0])
                    conf = float(proba[0, rt_idx])
                else:
                    conf = float(np.max(proba[0]))
            except Exception:
                log.warning("predict_proba failed.")
        return str(label), conf

model_server = ModelServer(MODEL_DIR)

# -------------------------
# Endpoints
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_server.model is not None}

@app.post("/predict", response_model=PredictOut)
def predict(req: PredictIn):
    try:
        label, conf = model_server.predict(req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Inference failed: " + str(e))
    return PredictOut(klass=label, confidence=conf)

@app.get("/qos", response_model=QoSOut)
def qos(class_label: str = Query("Real-Time")):
    try:
        from qos_engine import get_qos_for_label
        policy = get_qos_for_label(class_label)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid class_label")
    return QoSOut(klass=class_label, qos=policy)

@app.get("/qos/all")
def qos_all():
    from qos_engine import get_all_qos
    return get_all_qos()

@app.get("/simulate", response_model=SimulateOut)
def simulate(count: int = Query(20, ge=1, le=500), with_predictions: bool = Query(True)):
    """
    Generate synthetic flows for demo. If with_predictions=true, also run model inference.
    """
    if generate_flows is None:
        raise HTTPException(status_code=500, detail="Synthetic flow generator not available.")

    try:
        raw_flows = generate_flows(n=count)
        data_out = []

        for item in raw_flows:
            record = {
                "label": item["label"],
                "features": item["features"],
            }
            if with_predictions:
                try:
                    pred_label, conf = model_server.predict(item["features"])
                    record["prediction"] = {"klass": pred_label, "confidence": conf}
                except Exception as e:
                    record["prediction_error"] = str(e)
            data_out.append(record)

        return SimulateOut(count=len(data_out), with_predictions=with_predictions, data=data_out)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate flows: " + str(e))
