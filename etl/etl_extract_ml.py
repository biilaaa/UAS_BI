# etl/etl_extract_ml.py – EXTRACT DATA UNTUK ML DARI FACT LANGSUNG (OPTION A)

import pandas as pd
import mysql.connector

def extract_from_dw():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="dw_heart",
        port=3306
    )

    query = """
        SELECT
            Umur AS umur,
            Gender_Numeric AS gender,
            Jenis_Nyeri_Dada AS cp,
            Tekanan_Darah_Saat_Istirahat AS trestbps,
            Kadar_Kolesterol AS chol,
            Kadar_Gula_Darah AS fbs,
            Hasil_EKG AS restecg,
            Detak_Jantung_Maksimal AS thalach,
            Angina_Akibat_Olahraga AS exang,
            Depresi_ST AS oldpeak,
            Kemiringan_ST AS slope,
            Jumlah_Pembuluh_Darah AS ca,
            Thallium_Stress_Test AS thal,
            Hasil_Diagnosis AS target
        FROM Fact_Pasien_Jantung;
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    df = extract_from_dw()
    print(df.head())
    print(df.shape)
