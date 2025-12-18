import pandas as pd

def clean_dataset(df):
    df = df.copy()

    if "hasil_diagnosis" in df.columns:
        df["target"] = df["hasil_diagnosis"].astype(int)

    df = df.drop(columns=["hasil_diagnosis"], errors="ignore")

    df = df.fillna(df.median(numeric_only=True))

    return df


if __name__ == "__main__":
    from etl.etl_extract_ml import extract_from_dw

    df = extract_from_dw()
    df = clean_dataset(df)
    print(df.head())
    print("\nKolom dataset final:\n", df.columns.tolist())
