"""Email delivery helper for prediction notifications."""
from flask_mail import Message


def send_prediction_email(mail, app, recipient: str, disease: str, confidence: float, top3: list[tuple[str, float]]):
    """Sends a prediction summary email to the specified user."""
    if not recipient:
        return

    top_str = "\n".join([f"- {name}: {score:.2f}%" for name, score in top3])
    msg = Message(
        subject="Your Disease Prediction Result",
        recipients=[recipient],
        body=f"Predicted disease: {disease}\nConfidence: {confidence:.2f}%\nTop 3:\n{top_str}",
    )
    with app.app_context():
        mail.send(msg)
