"""Model training script for disease prediction classifiers."""
import os
import json
import pickle
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from utils.preprocess import load_and_preprocess_dataset
from utils.visualize import ensure_chart_dir, save_accuracy_bar, save_confusion_matrix, save_disease_distribution


DATASET_PATH = "dataset/disease_symptoms.csv"
MODEL_DIR = "models"
CHART_DIR = "static/images/charts"


def evaluate_predictions(y_true, y_pred):
    """Calculates weighted evaluation metrics for a prediction output."""
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }


def train_and_select_model():
    """Trains four models, evaluates performance, and persists the best performer."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    ensure_chart_dir(CHART_DIR)

    df, X, y, encoder, scaler, symptom_cols = load_and_preprocess_dataset(DATASET_PATH)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    configs = {
        "Decision Tree": (DecisionTreeClassifier(random_state=42), {"max_depth": [3, 5, 10, None], "min_samples_split": [2, 4, 8]}),
        "Naive Bayes": (GaussianNB(), {"var_smoothing": [1e-9, 1e-8, 1e-7]}),
        "KNN": (KNeighborsClassifier(), {"n_neighbors": [3, 5, 7], "weights": ["uniform", "distance"]}),
        "Random Forest": (RandomForestClassifier(random_state=42), {"n_estimators": [50, 100], "max_depth": [5, 10, None]}),
    }

    fitted_models = {}
    metrics = {}

    for name, (model, params) in configs.items():
        grid = GridSearchCV(model, params, cv=3, scoring="accuracy", n_jobs=-1)
        grid.fit(X_train, y_train)
        best_model = grid.best_estimator_
        y_pred = best_model.predict(X_test)
        fitted_models[name] = best_model
        metrics[name] = evaluate_predictions(y_test, y_pred)
        save_confusion_matrix(best_model, X_test, y_test, encoder.classes_, f"{CHART_DIR}/{name.lower().replace(' ', '_')}_cm.png")

    best_name = max(metrics, key=lambda n: metrics[n]["accuracy"])
    payload = {
        "model_name": best_name,
        "model": fitted_models[best_name],
        "label_encoder": encoder,
        "scaler": scaler,
        "symptom_columns": symptom_cols,
        "metrics": metrics,
    }

    with open(f"{MODEL_DIR}/best_model.pkl", "wb") as f:
        pickle.dump(payload, f)

    with open(f"{MODEL_DIR}/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    save_accuracy_bar(metrics, f"{CHART_DIR}/accuracy_comparison.png")
    save_disease_distribution(df, f"{CHART_DIR}/disease_distribution.png")
    return payload


if __name__ == "__main__":
    train_and_select_model()
    print("Training complete. Best model saved to models/best_model.pkl")
