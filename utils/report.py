"""PDF report generation utilities."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def create_prediction_report(path: str, user_name: str, email: str, symptoms: list[str], prediction: str, confidence: float, top3: list[tuple[str, float]], explanation: str):
    """Creates and saves a PDF report for a prediction result."""
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#0d6efd"))
    c.drawString(50, h - 60, "Disease Prediction Report")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    y = h - 100
    lines = [
        f"Patient Name: {user_name}",
        f"Email: {email}",
        f"Symptoms: {', '.join(symptoms)}",
        f"Predicted Disease: {prediction}",
        f"Confidence: {confidence:.2f}%",
        f"Top 3 Predictions: {', '.join([f'{d} ({p:.2f}%)' for d, p in top3])}",
        f"Explainability: {explanation}",
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 22

    c.save()
