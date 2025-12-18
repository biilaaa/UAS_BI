import pandas as pd

FEATURE_METADATA = {
    "umur": {"type": "int", "min": 20, "max": 100, "description": "Umur pasien"},
    "gender": {
        "type": "category",
        "allowed": [0, 1],
        "labels": {0: "female", 1: "male"},
        "description": "Jenis kelamin pasien",
    },
    "cp": {"type": "int", "min": 0, "max": 3, "description": "Tipe nyeri dada"},
    "trestbps": {"type": "int", "min": 80, "max": 200, "description": "Tekanan darah istirahat"},
    "chol": {"type": "int", "min": 100, "max": 600, "description": "Kadar kolesterol"},
    "fbs": {"type": "int", "allowed": [0, 1], "description": "Gula darah >120 mg/dl"},
    "restecg": {"type": "int", "min": 0, "max": 2, "description": "Hasil EKG"},
    "thalach": {"type": "int", "min": 60, "max": 220, "description": "Detak jantung maksimal"},
    "exang": {"type": "int", "allowed": [0, 1], "description": "Angina akibat olahraga"},
    "oldpeak": {"type": "float", "min": 0.0, "max": 10.0, "description": "Depresi ST"},
    "slope": {"type": "int", "min": 0, "max": 2, "description": "Kemiringan segmen ST"},
    "ca": {"type": "int", "min": 0, "max": 3, "description": "Jumlah pembuluh utama"},
    "thal": {"type": "int", "min": 0, "max": 3, "description": "Thallium stress test"},
}

def validate_input(df: pd.DataFrame):
    errors = []
    for col, rules in FEATURE_METADATA.items():
        val = df[col].iloc[0]

        if rules["type"] in ("int", "float"):
            if "min" in rules and val < rules["min"]:
                errors.append(f"{col} kurang dari minimum ({rules['min']})")
            if "max" in rules and val > rules["max"]:
                errors.append(f"{col} melebihi maksimum ({rules['max']})")

        if rules["type"] == "category":
            if val not in rules["allowed"]:
                errors.append(f"{col} nilai tidak valid ({val})")

    return errors

def mask_sensitive_data(df: pd.DataFrame):
    masked = df.copy()
    masked["umur"] = "***"    
    return masked

def readable_feature_name(col: str):
    mapping = {
        "umur": "Umur (tahun)",
        "gender": "Jenis Kelamin",
        "cp": "Jenis Nyeri Dada (0–3)",
        "trestbps": "Tekanan Darah Istirahat (mmHg)",
        "chol": "Kadar Kolesterol (mg/dl)",
        "fbs": "Gula Darah > 120 mg/dl (0/1)",
        "restecg": "Hasil EKG (0–2)",
        "thalach": "Detak Jantung Maksimal (bpm)",
        "exang": "Angina Akibat Olahraga (0/1)",
        "oldpeak": "Depresi ST",
        "slope": "Kemiringan ST (0–2)",
        "ca": "Jumlah Pembuluh Darah Utama (0–3)",
        "thal": "Thallium Stress Test (0–3)",
    }
    return mapping.get(col, col)
