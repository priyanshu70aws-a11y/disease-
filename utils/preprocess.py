"""Preprocessing helpers for dataset cleaning and feature preparation."""
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler


def load_and_preprocess_dataset(dataset_path: str):
    """Loads the dataset, handles missing values, and prepares normalized features and labels."""
    df = pd.read_csv(dataset_path)
    df = df.fillna(0)

    symptom_cols = [c for c in df.columns if c != "disease"]
    for col in symptom_cols:
        df[col] = df[col].apply(lambda x: 1 if str(x).strip().lower() in {"1", "yes", "true"} else (0 if str(x).strip().lower() in {"0", "no", "false"} else int(float(x))))

    scaler = MinMaxScaler()
    X = pd.DataFrame(scaler.fit_transform(df[symptom_cols]), columns=symptom_cols)

    le = LabelEncoder()
    y = le.fit_transform(df["disease"])
    return df, X, y, le, scaler, symptom_cols
