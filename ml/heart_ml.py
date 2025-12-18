from etl.etl_extract_ml import extract_from_dw
from ml.train_model import train_models

print("📌 Mengambil data dari DW...")
df = extract_from_dw()

print("📌 Melatih model...")
train_models(df)
