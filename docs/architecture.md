# System Architecture

CATO follows a **modular, layered architecture** designed for scalability, maintainability, and edge deployment.

## High-Level Diagram

![CATO Architecture Diagram](images/architecture.png)



## Component Breakdown

### 1. Frontend: React Dashboard
- **Framework**: React + Vite
- **Purpose**: Real-time visualization of multi-UE traffic
- **Features**:
  - Live classification display
  - Confidence scores
  - QoS recommendations
  - Log export (CSV)
  - Responsive design

> 📁 Path: `src/frontend/`

---

### 2. Backend: FastAPI Inference Engine
- **Framework**: FastAPI (Python)
- **Role**: Serve predictions, manage data, expose REST API
- **Key Endpoints**:
  | Endpoint | Function |
  |--------|---------|
  | `POST /predict` | Returns predicted app class and confidence |
  | `GET /qos?class_label=...` | Returns QoS policy for a class |
  | `GET /test-website` | Loads real test data from `website_testing.csv` |

> 📁 Path: `src/backend/main.py`

---

### 3. Machine Learning Model
- **Algorithm**: Random Forest Classifier
- **Training Data**: `Samsung_dataset.csv` (41K+ flows)
- **Features Used**:
  - `Flow.Duration`
  - `Total.Fwd.Packets`, `Total.Backward.Packets`
  - `Flow.Packets.s`
  - `Fwd.Packet.Length.Max`, `Bwd.Packet.Length.Max`
  - `Flow.IAT.Max`
  - `Init_Win_bytes_forward`, `Init_Win_bytes_backward`
- **Preprocessing**: StandardScaler + LabelEncoder
- **Export Format**: `joblib` (`.pkl`)

> 📁 Path: `model/multi_model.pkl`, `multi_scaler.pkl`, `multi_label_encoder.pkl`

---

### 4. QoS Policy Engine
- **Rule-Based Mapping**: Converts predicted class to QoS policy
- **Policies Include**:
  - Latency
  - Jitter
  - Bandwidth
  - Priority

| Application | Latency | Bandwidth | Priority |
|-----------|--------|----------|----------|
| Gaming | very_low | medium | very_high |
| Video Conferencing | low | guaranteed | high |
| Web Browsing | medium | best_effort | low_to_medium |

> 📁 Path: `src/backend/qos_engine.py`

---

### 5. Data Layer
- **Training Data**: `Samsung_dataset.csv` — used offline
- **Test Data**: `website_testing.csv` — loaded at runtime for real predictions
- **No Synthetic Flows** — only real-world data used in demo

> 📁 Path: `data/website_testing.csv`

---

### 6. Deployment
- **Local Execution**: No cloud, no third-party APIs
- **Docker-Ready**: Can be containerized for consistency
- **No Persistent DB**: Logs stored in memory (for demo)

---

> 🔗 [Back to README](../README.md)
