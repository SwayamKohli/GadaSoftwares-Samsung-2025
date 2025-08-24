from __future__ import annotations

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from joblib import load

from .qos_engine import get_qos_for_label, get_all_qos

# Allow importing data.synthetic_flows
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "model"
sys.path.append(str(DATA_DIR))
try:
    from synthetic_flows import generate_flows  # type: ignore
except Exception:
    generate_flows = None  # noqa


# -------------------------
# App + CORS
# -------------------------
app = FastAPI(
    title="Traffic Classifier Backend",
    description="FastAPI backend for Real-Time vs Non-Real-Time classification + QoS policies.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
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
    features: Dict[str, float] = Field(
        ..., description="Mapping of feature name -> numeric value."
    )

    @validator("features")
    def _non_empty(cls, v):
        if not v:
            raise ValueError("features must not be empty")
        if not all(isinstance(x, (int, float)) for x in v.values()):
            raise ValueError("features must contain only numeric values")
        return v


class PredictOut(BaseModel):
    klass: str = Field(..., description='Predicted class label: "Real-Time" or "Non-Real-Time"')
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Model probability if available (0..1).")


class QoSOut(BaseModel):
    klass: str
    qos: Dict[str, Any]


class SimulateOut(BaseModel):
    count: int
    with_predictions: bool
    data: List[Dict[str, Any]]


# -------------------------
# Model Loader
# -------------------------
class DummyModel:
    """
    Very simple, deterministic rule-based fallback:
    - Treat flows with small iat & jitter and smaller packet size as Real-Time.
    """

    classes_ = np.array(["Non-Real-Time", "Real-Time"])

    def predict(self, X: np.ndarray) -> np.ndarray:
        # Heuristic: RT if (flow_iat_mean_ms < 25 and flow_iat_std_ms < 12) or avg_pkt_size < 350
        # columns order will be handled upstream; here we use column names if provided.
        # If not provided, use positional heuristic.
        return np.where(
            ((X[:, self._col("flow_iat_mean_ms")] < 25) &
             (X[:, self._col("flow_iat_std_ms")] < 12)) |
            (X[:, self._col("avg_pkt_size")] < 350),
            "Real-Time", "Non-Real-Time"
        )

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        # Soft confidence based on iat mean & std
        score = 1.0 / (1.0 + np.exp((X[:, self._col("flow_iat_mean_ms")] - 25) / 10))
        score *= 1.0 / (1.0 + np.exp((X[:, self._col("flow_iat_std_ms")] - 12) / 5))
        # Clamp and make 2-class distribution
        p_rt = np.clip(score, 0.05, 0.95)
        return np.vstack([1 - p_rt, p_rt]).T

    def _col(self, name: str) -> int:
        # set at runtime by ModelServer once feature_names are known
        return self.feature_index[name]  # type: ignore


class ModelServer:
    def __init__(self, model_dir: Path):
        self.model = None
        self.scaler = None
        self.feature_names: Optional[List[str]] = None
        self._load(model_dir)

    def _load(self, model_dir: Path):
        model_path = model_dir / "model.pkl"
        scaler_path = model_dir / "scaler.pkl"

        if model_path.exists():
            try:
                self.model = load(model_path)
                log.info(f"Loaded model from {model_path}")
            except Exception as e:
                log.exception("Failed to load model.pkl, using DummyModel.")
                self.model = DummyModel()
        else:
            log.warning("model.pkl not found, using DummyModel.")
            self.model = DummyModel()

        if scaler_path.exists():
            try:
                self.scaler = load(scaler_path)
                log.info(f"Loaded scaler from {scaler_path}")
            except Exception:
                log.exception("Failed to load scaler.pkl; proceeding without scaler.")
                self.scaler = None
        else:
            log.warning("scaler.pkl not found; proceeding without scaler.")
            self.scaler = None

        # Determine feature list/order
        if self.scaler is not None and hasattr(self.scaler, "feature_names_in_"):
            self.feature_names = list(self.scaler.feature_names_in_)  # type: ignore
            log.info(f"Feature order from scaler: {self.feature_names}")
        elif self.model is not None and hasattr(self.model, "feature_names_in_"):
            self.feature_names = list(self.model.feature_names_in_)  # type: ignore
            log.info(f"Feature order from model: {self.feature_names}")
        else:
            # Fallback: we will infer at request time from payload keys (sorted).
            self.feature_names = None

        # If DummyModel, prepare its name->index map once we know features (done per-request)
        if isinstance(self.model, DummyModel):
            log.info("Initialized DummyModel fallback.")

    def _vectorize(self, features: Dict[str, float]) -> np.ndarray:
        # Decide on column order
        if self.feature_names is None:
            # Infer a stable order from payload keys (sorted); OK for dev/demo
            self.feature_names = sorted(features.keys())
            log.info(f"Inferred feature order from payload: {self.feature_names}")

        # Create row in the expected order, filling missing with 0 and ignoring extras
        row = [float(features.get(f, 0.0)) for f in self.feature_names]

        X = np.array([row], dtype=float)

        # Scale if scaler is available
        if self.scaler is not None:
            try:
                X = self.scaler.transform(X)
            except Exception as e:
                log.error(f"Scaler.transform failed: {e}. Proceeding unscaled.")

        # Attach name->index for DummyModel
        if isinstance(self.model, DummyModel):
            self.model.feature_index = {n: i for i, n in enumerate(self.feature_names)}  # type: ignore

        return X

    def predict(self, features: Dict[str, float]) -> (str, Optional[float]):
        if self.model is None:
            raise RuntimeError("Model not initialized.")

        X = self._vectorize(features)

        # predict label
        try:
            y = self.model.predict(X)
            if isinstance(y, np.ndarray):
                label = str(y[0])
            else:
                label = str(y)
        except Exception as e:
            log.exception("Model.predict failed.")
            raise

        # confidence if available
        conf: Optional[float] = None
        if hasattr(self.model, "predict_proba"):
            try:
                proba = self.model.predict_proba(X)
                # attempt to locate RT index if class order known
                classes = getattr(self.model, "classes_", np.array(["Non-Real-Time", "Real-Time"]))
                if "Real-Time" in classes:
                    rt_idx = int(np.where(classes == "Real-Time")[0][0])
                    conf = float(proba[0, rt_idx])
                else:
                    conf = float(np.max(proba[0]))
            except Exception:
                log.warning("predict_proba failed; confidence omitted.")
                conf = None

        return label, conf


model_server = ModelServer(MODEL_DIR)

# -------------------------
# Endpoints
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_server.model is not None}


@app.post("/predict", response_model=PredictOut)
def predict(req: PredictIn):
    """
    Accepts a JSON of feature_name -> value and returns:
    {
      "klass": "Real-Time" | "Non-Real-Time",
      "confidence": 0.94   # if available
    }
    """
    try:
        label, conf = model_server.predict(req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference failed: {e}")

    return PredictOut(klass=label, confidence=conf)


@app.get("/qos", response_model=QoSOut)
def qos(class_label: str = Query("Real-Time", description="Label to fetch QoS for")):
    """
    Returns QoS policy for "Real-Time" or "Non-Real-Time".
    """
    try:
        policy = get_qos_for_label(class_label)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid class_label")
    return QoSOut(klass=class_label, qos=policy)


@app.get("/qos/all")
def qos_all():
    """Return both policies to help the frontend cache."""
    return get_all_qos()


@app.get("/simulate", response_model=SimulateOut)
def simulate(count: int = Query(20, ge=1, le=500),
             with_predictions: bool = Query(True, description="Also run the model over generated flows")):
    """
    Generate synthetic flows for demo. If with_predictions=true, also include model predictions.
    """
    if generate_flows is None:
        raise HTTPException(status_code=500, detail="Synthetic generator not available.")

    flows = generate_flows(n=count)
    data_out: List[Dict[str, Any]] = []

    for item in flows:
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
