# Installation Guide

This guide walks you through setting up **CATO** (Classification of Application Traffic Online) locally.

## Prerequisites
- Python 3.8+
- Node.js 16+
- Git
- Windows / Linux / macOS

## Step 1: Clone the Repository
```bash
git clone https://github.com/SwayamKohli/samsung-2025.git
cd samsung-2025
```

## Step 2: Set Up Backend
Navigate to backend
cd src/backend

Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate    # Windows
### venv/bin/activate      # Linux/Mac

Install required packages
pip install fastapi uvicorn scikit-learn pandas joblib pickle5

## Step 3: Set Up Frontend 
Go to frontend
cd ../frontend

Install dependencies
npm install

## Step 4: Download Model & Dataset (Hugging Face)

The model and test data are not in Git (due to .gitignore). Download them from Hugging Face: 
Model: multi_model.pkl, multi_scaler.pkl, multi_label_encoder.pkl 

🔗 [https://huggingface.co/GadaSoftware/CATO-MultiClass-RF  
](https://huggingface.co/ArcFR/Network_Traffic_Classifer/tree/main)

Save to: model/ 
Dataset: website_testing.csv 

- 🔗 https://www.kaggle.com/datasets/jsrojas/ip-network-traffic-flows-labeled-with-87-apps 
- 🔗 https://www.kaggle.com/datasets/kimdaegyeom/5g-traffic-datasets/data

Save to: data/ 

## Step 5: Start Backend 
```bash
cd src/backend
uvicorn main:app --reload --port 8000
```

You should see: 
```bash
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```
 ## Step 6: Start Frontend 
 ```bash
cd src/frontend
npm run dev
```
Open: http://localhost:5173  

## Step 7: Verify Functionality 

- Visit http://localhost:8000/docs  (Swagger UI)
- Test POST /predict with sample features
- Check frontend dashboard updates every 2 seconds
- Confirm logs show real predictions from website_testing.csv  
