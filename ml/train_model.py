import pickle
import json
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

MODEL_DIR = "models"
MODEL_LR = os.path.join(MODEL_DIR, "model_lr.pkl")
MODEL_RF = os.path.join(MODEL_DIR, "model_rf.pkl")
METRICS_FILE = os.path.join(MODEL_DIR, "metrics.json")


def train_models(df):

    if df is None or len(df) == 0:
        print("❌ ERROR: DataFrame kosong! Tidak bisa melatih model.")
        return

    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.fillna(0)

    if "target" not in df.columns:
        print("❌ ERROR: Kolom 'target' tidak ditemukan!")
        print("Kolom yang ada:", df.columns.tolist())
        return

    X = df.drop("target", axis=1)
    y = df["target"]

    if len(X) == 0:
        print("❌ ERROR: Dataset kosong setelah drop target.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    lr = LogisticRegression(max_iter=3000)
    lr.fit(X_train, y_train)
    pred_lr = lr.predict(X_test)
    acc_lr = accuracy_score(y_test, pred_lr)

    rf = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        max_depth=None
    )
    rf.fit(X_train, y_train)
    pred_rf = rf.predict(X_test)
    acc_rf = accuracy_score(y_test, pred_rf)

    os.makedirs(MODEL_DIR, exist_ok=True)

    with open(MODEL_LR, "wb") as f:
        pickle.dump(lr, f)

    with open(MODEL_RF, "wb") as f:
        pickle.dump(rf, f)

    metrics = {
        "lr_acc": float(acc_lr),
        "rf_acc": float(acc_rf),
    }

    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=4)

    print("🎉 Model & metrics berhasil disimpan!")
