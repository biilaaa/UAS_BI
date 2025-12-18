from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from app.data_governance import validate_input
import os

# =========================
# Path model untuk Docker
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

model_rf = joblib.load(os.path.join(MODEL_DIR, "model_rf.pkl"))
model_lr = joblib.load(os.path.join(MODEL_DIR, "model_lr.pkl"))

app = FastAPI(title="Heart Disease Prediction API")

# =========================
# Schema Input API
# =========================
class PatientData(BaseModel):
    umur: int
    gender: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

@app.get("/")
def home():
    return {"message": "Heart Disease Prediction API is running"}

@app.post("/predict")
def predict(data: PatientData):

    df = pd.DataFrame([data.dict()])

    # Validasi data governance
    errors = validate_input(df)
    if errors:
        return {"status": "error", "errors": errors}

    # Jika kamu punya fungsi mask_sensitive_data, pastikan import-nya ada
    try:
        masked = mask_sensitive_data(df)
    except:
        masked = df  # fallback jika tidak ada fungsi

    pred_rf = int(model_rf.predict(df)[0])
    prob_rf = model_rf.predict_proba(df)[0].tolist()

    pred_lr = int(model_lr.predict(df)[0])

    return {
        "input_masked": masked.to_dict(orient="records")[0],
        "prediction_rf": pred_rf,
        "probability_rf": prob_rf,
        "prediction_lr": pred_lr,
    }
