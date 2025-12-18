import os
import pandas as pd
import numpy as np


def load_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "processed", "heart_clean.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File dataset tidak ditemukan: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"File loaded: {os.path.abspath(csv_path)}")
    print(f"Jumlah baris: {df.shape[0]}")
    print(f"Jumlah kolom: {df.shape[1]}")
    print()
    return df


def check_missing(df):
    print("=== Missing Values ===")
    print(df.isnull().sum())
    print()


def detect_outliers(df):
    print("=== Outlier Detection (Z-Score) ===")
    outlier_counts = {}

    for col in df.select_dtypes(include=[np.number]).columns:
        z = np.abs((df[col] - df[col].mean()) / df[col].std())
        outlier_counts[col] = int((z > 3).sum())

    print(outlier_counts)
    print()


def governance_validation(df):
    print("=== Validation Using Data Governance Rules ===")
    issues = 0

    if df.isnull().sum().sum() > 0:
        issues += 1

    if issues:
        print("❌ Ditemukan baris bermasalah berdasarkan aturan governance.")
    else:
        print("✅ Data memenuhi aturan data governance.")

    print()


if __name__ == "__main__":
    print("=" * 60)
    print("📌 QUALITY REPORT — DATA WAREHOUSE")
    print("=" * 60)
    print()

    df = load_dataset()

    check_missing(df)
    detect_outliers(df)
    governance_validation(df)

    print("✅ Quality Report Selesai Dibuat.")
