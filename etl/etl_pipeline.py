import pandas as pd
from sqlalchemy import create_engine
import os

FILE = r"D:\SEMESTER 5\BI\UAS\DWHEART\data\raw\Heart Disease Dataset fix.xlsx"
CSV_OUTPUT = r"D:\SEMESTER 5\BI\UAS\DWHEART\data\processed\heart_clean.csv"

user = "root"
password = ""  
host = "127.0.0.1"
database = "dw_heart"

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

print("=== EXTRACT DATA ===")
df = pd.read_excel(FILE)
print("Jumlah data (raw):", df.shape)

print("\n=== TRANSFORM DATA ===")

df.columns = [c.lower().replace(" ", "_") for c in df.columns]

df = df.fillna(df.median(numeric_only=True))

if "age" in df.columns and "chol" in df.columns:
    df["age_chol_ratio"] = df["age"] / (df["chol"] + 1)

print("Jumlah data setelah transform:", df.shape)

print("\n=== SAVE TO CSV (PROCESSED) ===")
os.makedirs(os.path.dirname(CSV_OUTPUT), exist_ok=True)

df.to_csv(CSV_OUTPUT, index=False)
print(f"CSV processed disimpan ke: {CSV_OUTPUT}")

print("\n=== LOAD TO DATA WAREHOUSE (MYSQL) ===")
df.to_sql("fact_heart", engine, if_exists="replace", index=False)
print(f"Berhasil load ke tabel 'fact_heart' di database '{database}'")

print("\n=== ETL SELESAI ===")
