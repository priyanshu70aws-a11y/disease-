"""Visualization helpers for model evaluation outputs."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import ConfusionMatrixDisplay


def ensure_chart_dir(path: str):
    """Ensures the chart output directory exists before image generation."""
    os.makedirs(path, exist_ok=True)


def save_accuracy_bar(metrics: dict, output_path: str):
    """Saves a bar chart comparing model accuracies."""
    plt.figure(figsize=(8, 5))
    names = list(metrics.keys())
    accs = [m["accuracy"] for m in metrics.values()]
    sns.barplot(x=names, y=accs, palette="Blues_d")
    plt.ylim(0, 1)
    plt.title("Model Accuracy Comparison")
    plt.ylabel("Accuracy")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_confusion_matrix(model, X_test, y_test, labels, output_path: str):
    """Saves confusion matrix image for a trained classifier."""
    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, display_labels=labels, cmap="Blues", ax=ax, xticks_rotation=45)
    disp.ax_.set_title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_disease_distribution(df, output_path: str):
    """Saves a pie chart showing disease class distribution."""
    plt.figure(figsize=(7, 7))
    counts = df["disease"].value_counts()
    plt.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=140)
    plt.title("Disease Distribution")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
