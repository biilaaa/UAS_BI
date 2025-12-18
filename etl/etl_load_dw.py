import pandas as pd
import pymysql
from datetime import datetime, timedelta
import os

EXCEL_FILE = r"D:\SEMESTER 5\BI\UAS\DWHEART\data\raw\Heart Disease Dataset fix.xlsx"
CSV_OUT    = r"D:\SEMESTER 5\BI\UAS\DWHEART\data\processed\heart_clean.csv"

MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASS = ""
MYSQL_DB   = "dw_heart"
MYSQL_PORT = 3306

BASE_DATE = datetime.today().date()

print(f"📌 Membaca file: {EXCEL_FILE}")
df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
print("📌 Ukuran awal:", df.shape)

df.columns = (
    df.columns.str.strip()
              .str.lower()
              .str.replace(" ", "_")
              .str.replace("(", "")
              .str.replace(")", "")
              .str.replace("/", "_")
              .str.replace(">", "")
)

print("📌 Kolom setelah normalisasi:", list(df.columns))

rename_fix = {
    "waktu_perawatan_hari_": "waktu_perawatan_hari",
}
df = df.rename(columns=rename_fix)

if "meninggal" in df.columns:
    df["meninggal"] = df["meninggal"].replace({
        "Dead": 1,
        "Alive": 0,
        "dead": 1,
        "alive": 0
    })

for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col] = df[col].fillna(df[col].median())
    else:
        df[col] = df[col].fillna("unknown")


mapping = {
    "age":         "umur",
    "sex":         "gender",
    "cp":          "jenis_nyeri_dada",
    "trestbps":    "tekanan_darah_saat_istirahat",
    "chol":        "kadar_kolesterol",
    "fbs":         "kadar_gula_darah__120_mg_dl", 
    "restecg":     "hasil_ekg",
    "thalach":     "detak_jantung_maksimal",
    "exang":       "angina_akibat_olahraga",
    "oldpeak":     "depresi_st",
    "slope":       "kemiringan_puncak_segmen_st",
    "ca":          "jumlah_pembuluh_darah_utama",
    "thal":        "thallium_stress_test",
    "target":      "hasil_diagnosis",
    "time":        "waktu_perawatan_hari",
    "death_event": "meninggal"
}

print("📌 Mapping final:", mapping)


os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)
df.to_csv(CSV_OUT, index=False)
print(f"📌 CSV disimpan: {CSV_OUT}")

conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    db=MYSQL_DB,
    port=MYSQL_PORT,
    charset="utf8mb4",
    autocommit=False
)
cur = conn.cursor()

print("📌 Mengosongkan tabel DW...")

tables = [
    "Fact_Pasien_Jantung",
    "Dim_Pasien",
    "Dim_Waktu",
    "Dim_Riwayat",
    "Dim_EKG",
    "Dim_Stres",
    "Dim_Tes",
    "Dim_Diagnosis",
    "Dim_Kematian"
]

cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
for t in tables:
    try:
        cur.execute(f"TRUNCATE TABLE {t}")
    except Exception as e:
        print(f"❌ Gagal truncate {t}: {e}")
cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("✅ Semua tabel DW dikosongkan.\n")


def col(row, key):
    colname = mapping.get(key)
    if colname not in row.index:
        return None
    return row[colname]


rows_total = df.shape[0]
count = 0
print("📌 Mulai insert data...")

for idx, row in df.iterrows():
    try:
       
        umur     = int(col(row, "age"))
        sex_val  = int(col(row, "sex"))         
        cp       = int(col(row, "cp"))
        trestbps = float(col(row, "trestbps"))
        chol     = float(col(row, "chol"))
        fbs      = int(col(row, "fbs"))        
        restecg  = int(col(row, "restecg"))
        thalach  = float(col(row, "thalach"))
        exang    = int(col(row, "exang"))
        oldpeak  = float(col(row, "oldpeak"))
        slope    = int(col(row, "slope"))
        ca       = int(col(row, "ca"))
        thal     = int(col(row, "thal"))
        target   = int(col(row, "target"))
        los      = int(col(row, "time"))         
        death_ev = int(col(row, "death_event"))  

        
        cur.execute("""
            INSERT INTO Dim_Riwayat (Kadar_Gula_Darah, Tekanan_Darah_Istirahat, Kadar_Kolesterol)
            VALUES (%s,%s,%s)
        """, (fbs, trestbps, chol))
        id_riwayat = cur.lastrowid

   
        cur.execute("""
            INSERT INTO Dim_EKG (Hasil_EKG, Detak_Jantung_Maksimal)
            VALUES (%s,%s)
        """, (restecg, thalach))
        id_ekg = cur.lastrowid

        
        cur.execute("""
            INSERT INTO Dim_Stres (Depresi_ST, Kemiringan_ST, Thallium_Stress_Test, Jumlah_Pembuluh_Darah)
            VALUES (%s,%s,%s,%s)
        """, (oldpeak, slope, thal, ca))
        id_stres = cur.lastrowid

        cur.execute("""
            INSERT INTO Dim_Tes (Jenis_Nyeri_Dada, Angina_Akibat_Olahraga, ID_EKG, ID_Stres)
            VALUES (%s,%s,%s,%s)
        """, (cp, exang, id_ekg, id_stres))
        id_tes = cur.lastrowid

        cur.execute("""
            INSERT INTO Dim_Diagnosis (Hasil_Diagnosis)
            VALUES (%s)
        """, (target,))
        id_diag = cur.lastrowid

        tanggal_masuk = (BASE_DATE - timedelta(days=los)).strftime("%Y-%m-%d")
        kategori = "Singkat" if los < 3 else ("Sedang" if los <= 7 else "Lama")

        cur.execute("""
            INSERT INTO Dim_Waktu (Tanggal_Masuk, Lama_Perawatan, Kategori_Waktu)
            VALUES (%s,%s,%s)
        """, (tanggal_masuk, los, kategori))
        id_waktu = cur.lastrowid

        status = "Dead" if death_ev == 1 else "Alive"
        cur.execute("""
            INSERT INTO Dim_Kematian (Status_Kematian)
            VALUES (%s)
        """, (status,))
        id_kematian = cur.lastrowid

        gender_str = "male" if sex_val == 1 else "female"
        cur.execute("""
            INSERT INTO Dim_Pasien (Umur, Gender, ID_Riwayat)
            VALUES (%s,%s,%s)
        """, (umur, gender_str, id_riwayat))
        id_pasien = cur.lastrowid

        cur.execute("""
            INSERT INTO Fact_Pasien_Jantung
            (
                ID_Pasien, ID_Waktu, ID_Riwayat, ID_Tes, ID_Diagnosis, ID_Kematian,
                Hasil_Diagnosis, Waktu_Perawatan_Hari, Status_Kematian,

                -- NILAI ORIGINAL UNTUK ML (TANPA JOIN)
                Umur, Gender_Numeric, Jenis_Nyeri_Dada, Tekanan_Darah_Saat_Istirahat,
                Kadar_Kolesterol, Kadar_Gula_Darah, Hasil_EKG, Detak_Jantung_Maksimal,
                Angina_Akibat_Olahraga, Depresi_ST, Kemiringan_ST, Jumlah_Pembuluh_Darah,
                Thallium_Stress_Test
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,
                %s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )
        """, (
            id_pasien, id_waktu, id_riwayat, id_tes, id_diag, id_kematian,
            target, los, status,
            umur,
            sex_val,
            cp,
            trestbps,
            chol,
            fbs,
            restecg,
            thalach,
            exang,
            oldpeak,
            slope,
            ca,
            thal
        ))

        conn.commit()
        count += 1
        if count % 50 == 0:
            print(f"   → {count}/{rows_total} baris selesai...")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error baris {idx}: {e}")

print(f"\n🎉 Selesai! Total {count} baris masuk ke DW.")
cur.close()
conn.close()
print("📌 Koneksi MySQL ditutup.")
