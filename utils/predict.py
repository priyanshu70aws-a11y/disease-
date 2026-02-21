"""Prediction utilities for symptom parsing and model inference."""
import re
import numpy as np
import pandas as pd


def extract_symptoms_from_text(text: str, symptom_columns: list[str]) -> list[str]:
    """Extracts known symptom keywords from natural language user input."""
    cleaned = re.sub(r"[^a-zA-Z_ ]", " ", text.lower())
    normalized = cleaned.replace(" ", "_")
    hits = []
    for symptom in symptom_columns:
        if symptom.lower() in normalized or symptom.lower().replace("_", " ") in cleaned:
            hits.append(symptom)
    return sorted(set(hits))


def vectorize_symptoms(selected_symptoms: list[str], symptom_columns: list[str]) -> pd.DataFrame:
    """Converts selected symptoms into a binary one-row dataframe for prediction."""
    symptom_set = set(selected_symptoms)
    row = [1 if col in symptom_set else 0 for col in symptom_columns]
    return pd.DataFrame([row], columns=symptom_columns)


def predict_top_3(model, encoder, input_df: pd.DataFrame):
    """Returns top-3 disease predictions with confidence percentages."""
    probabilities = model.predict_proba(input_df)[0]
    top_idx = np.argsort(probabilities)[::-1][:3]
    top = [(encoder.inverse_transform([idx])[0], float(probabilities[idx]) * 100) for idx in top_idx]
    best = top[0]
    return best, top


def explain_prediction(model, symptom_columns: list[str], selected_symptoms: list[str]) -> str:
    """Builds a simple explainability message using tree-based feature importances when available."""
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return f"Prediction was primarily driven by reported symptoms: {', '.join(selected_symptoms)}."

    pairs = sorted(zip(symptom_columns, importances), key=lambda x: x[1], reverse=True)
    selected = [p for p in pairs if p[0] in set(selected_symptoms)][:5]
    if not selected:
        return "The model used all symptom interactions to produce this prediction."
    detail = ", ".join([f"{name} ({score:.2f})" for name, score in selected])
    return f"Most influential entered symptoms: {detail}."
