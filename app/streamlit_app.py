import os
import json
import pickle

import pandas as pd
import streamlit as st

from ui_components import show_header, show_result_card, export_pdf
from charts import show_probability_animation

MODEL_PATH_LR = "models/model_lr.pkl"
MODEL_PATH_RF = "models/model_rf.pkl"
METRICS_PATH = "models/metrics.json"


def load_model(path: str):
    if not os.path.exists(path):
        st.error(f"❌ File model tidak ditemukan: {path}")
        return None
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"❌ Gagal load model {path}: {e}")
        return None


logreg_model = load_model(MODEL_PATH_LR)
rf_model = load_model(MODEL_PATH_RF)

metrics = {}
if os.path.exists(METRICS_PATH):
    try:
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)
    except Exception as e:
        st.error(f"❌ Gagal load metrics.json: {e}")


st.set_page_config(
    page_title="Prediksi Penyakit Jantung",
    page_icon="❤️",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #e9f4ff;
        }

        .block-container {
            max-width: 1100px;
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
        }

        h1, h2, h3, h4 {
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
        }

        div[data-testid="stMetric"] {
            background-color: transparent !important;
            border: none !important;
        }

        .stButton>button {
            background-color: #2563eb;
            color: white;
            border-radius: 999px;
            padding: 0.5rem 1.4rem;
            border: none;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
        }

        div[data-baseweb="input"] > div {
            background-color: #dbeafe;
            border-radius: 10px;
            border: 1px solid #bfdbfe;
        }
        div[data-baseweb="select"] > div {
            background-color: #dbeafe;
            border-radius: 10px !important;
            border: 1px solid #bfdbfe;
        }

        .center-title {
            text-align: center;
            margin-top: 2rem;
            margin-bottom: 0.3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

show_header()

st.markdown("### 📊 Akurasi Model")

lr_acc = metrics.get("lr_acc")
rf_acc = metrics.get("rf_acc")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Logistic Regression**")
    if lr_acc is not None:
        st.metric("Accuracy", f"{lr_acc * 100:.0f} %")
    else:
        st.metric("Accuracy", "-")

with col2:
    st.markdown("**Random Forest**")
    if rf_acc is not None:
        st.metric("Accuracy", f"{rf_acc * 100:.0f} %")
    else:
        st.metric("Accuracy", "-")

st.markdown("---")

st.markdown("### 🧪 Masukkan Data Pasien")

col_a, col_b = st.columns(2)

with col_a:
    umur = st.number_input("Umur", 20, 100, 40)
    gender_input = st.selectbox("Gender", ["male", "female"])
    gender = 1 if gender_input == "male" else 0

    cp = st.selectbox("Jenis Nyeri Dada (0–3)", [0, 1, 2, 3])
    trestbps = st.number_input("Tekanan Darah Saat Istirahat", 80, 200, 120)
    chol = st.number_input("Kadar Kolesterol", 100, 600, 250)
    fbs = st.selectbox("Kadar Gula Darah > 120 mg/dl (1 = Ya, 0 = Tidak)", [0, 1])

with col_b:
    restecg = st.selectbox("Hasil EKG (0–2)", [0, 1, 2])
    thalach = st.number_input("Detak Jantung Maksimal", 60, 220, 150)
    exang = st.selectbox("Angina Akibat Olahraga? (1 = Ya, 0 = Tidak)", [0, 1])
    oldpeak = st.number_input("Depresi ST", 0.0, 10.0, 1.5)
    slope = st.selectbox("Kemiringan ST (0–2)", [0, 1, 2])
    ca = st.selectbox("Jumlah Pembuluh Darah Utama (0–3)", [0, 1, 2, 3])

thal = st.selectbox("Thallium Stress Test (0–3)", [0, 1, 2, 3])

input_data = pd.DataFrame(
    [
        {
            "umur": umur,
            "gender": gender,
            "cp": cp,
            "trestbps": trestbps,
            "chol": chol,
            "fbs": fbs,
            "restecg": restecg,
            "thalach": thalach,
            "exang": exang,
            "oldpeak": oldpeak,
            "slope": slope,
            "ca": ca,
            "thal": thal,
        }
    ]
)

st.markdown("<h3 class='center-title'>🧾 Hasil Prediksi</h3>", unsafe_allow_html=True)

if st.button("🔍 Prediksi Penyakit Jantung"):

    if logreg_model is None or rf_model is None:
        st.error("❌ Model belum berhasil diload!")
    else:
        pred_lr = int(logreg_model.predict(input_data)[0])
        pred_rf = int(rf_model.predict(input_data)[0])

        show_result_card(pred_lr, pred_rf)

        st.markdown("### 📊 Visualisasi Probabilitas Risiko")
        prob_no_risk, prob_risk = show_probability_animation(rf_model, input_data)

        st.markdown("### 📄 Laporan Prediksi")

        pdf_path = export_pdf(
            input_data=input_data,
            pred_lr=pred_lr,
            pred_rf=pred_rf,
            prob_rf=[prob_no_risk, prob_risk],
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Laporan PDF",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
            )
