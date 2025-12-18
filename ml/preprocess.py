def preprocess(df):
    df["fbs"] = df["fbs"].astype(int)
    df["restecg"] = df["restecg"].astype(int)

    df["thal"] = df["thal"].replace({
        0: 1,  # normalisasi
        1: 1,
        2: 2,
        3: 3
    })

    return df
