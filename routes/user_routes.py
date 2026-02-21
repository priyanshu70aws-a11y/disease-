"""User-facing routes for authentication, prediction, and profile pages."""
import os
import json
import pickle
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_user, logout_user, login_required, current_user

from model import db, User, Prediction
from utils.predict import extract_symptoms_from_text, vectorize_symptoms, predict_top_3, explain_prediction
from utils.report import create_prediction_report
from utils.email import send_prediction_email

user_bp = Blueprint("user", __name__)


def role_required(*roles):
    """Restricts access to users whose role matches one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("You are not authorized to access this page.", "danger")
                return redirect(url_for("user.login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def load_model_artifact():
    """Loads the trained model payload from pickle storage."""
    model_path = os.path.join(current_app.root_path, "models", "best_model.pkl")
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as f:
        return pickle.load(f)


@user_bp.route("/")
def home():
    """Renders landing page for all visitors."""
    return render_template("home.html")


@user_bp.route("/about")
def about():
    """Renders project about page."""
    return render_template("about.html")


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handles new account creation with hashed password storage."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "Patient")

        if not all([name, email, password]):
            flash("All fields are required.", "warning")
            return redirect(url_for("user.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("user.register"))

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("user.login"))

    return render_template("register.html")


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticates users and starts a secure login session."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials.", "danger")
            return redirect(url_for("user.login"))

        login_user(user)
        flash("Logged in successfully.", "success")
        if user.role == "Admin":
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("user.dashboard"))

    return render_template("login.html")


@user_bp.route("/logout")
@login_required
def logout():
    """Logs out the current user and ends their session."""
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("user.home"))


@user_bp.route("/dashboard")
@login_required
@role_required("Patient", "Doctor")
def dashboard():
    """Renders the symptom entry dashboard."""
    artifact = load_model_artifact()
    symptom_columns = artifact["symptom_columns"] if artifact else []
    return render_template("dashboard.html", symptom_columns=symptom_columns)


@user_bp.route("/predict", methods=["POST"])
@login_required
@role_required("Patient", "Doctor")
def predict():
    """Runs disease prediction from selected symptoms and optional NLP text input."""
    artifact = load_model_artifact()
    if artifact is None:
        flash("Model not trained yet. Please run train_model.py.", "warning")
        return redirect(url_for("user.dashboard"))

    symptom_columns = artifact["symptom_columns"]
    selected_symptoms = request.form.getlist("symptoms")
    text_input = request.form.get("symptom_text", "").strip()

    if text_input:
        selected_symptoms.extend(extract_symptoms_from_text(text_input, symptom_columns))

    selected_symptoms = sorted(set(selected_symptoms))
    if not selected_symptoms:
        flash("Please enter at least one valid symptom.", "warning")
        return redirect(url_for("user.dashboard"))

    unknown = [s for s in selected_symptoms if s not in symptom_columns]
    if unknown:
        flash(f"Unrecognized symptoms ignored: {', '.join(unknown)}", "warning")
        selected_symptoms = [s for s in selected_symptoms if s in symptom_columns]

    input_df = vectorize_symptoms(selected_symptoms, symptom_columns)
    input_df = artifact["scaler"].transform(input_df)
    best, top3 = predict_top_3(artifact["model"], artifact["label_encoder"], input_df)
    explanation = explain_prediction(artifact["model"], symptom_columns, selected_symptoms)

    prediction = Prediction(
        user_id=current_user.id,
        symptoms=", ".join(selected_symptoms),
        predicted_disease=best[0],
        confidence=best[1],
        top_3=json.dumps(top3),
        explanation=explanation,
    )
    db.session.add(prediction)
    db.session.commit()

    if current_app.config.get("MAIL_SUPPRESS_SEND", True) is False:
        send_prediction_email(current_app.extensions["mail"], current_app, current_user.email, best[0], best[1], top3)

    flash("Prediction generated successfully.", "success")
    return render_template("result.html", prediction=prediction, top3=top3)


@user_bp.route("/history")
@login_required
@role_required("Patient", "Doctor")
def history():
    """Shows historical predictions for the logged-in user."""
    records = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).all()
    return render_template("history.html", records=records, json=json)


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Displays and updates profile information for the current user."""
    if request.method == "POST":
        current_user.name = request.form.get("name", current_user.name).strip()
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("user.profile"))
    return render_template("profile.html")


@user_bp.route("/evaluation")
@login_required
def evaluation():
    """Renders model metrics and generated chart assets."""
    artifact = load_model_artifact()
    metrics = artifact.get("metrics", {}) if artifact else {}
    return render_template("evaluation.html", metrics=metrics)


@user_bp.route("/report/<int:prediction_id>")
@login_required
def report(prediction_id):
    """Generates and serves PDF report for a selected prediction."""
    pred = Prediction.query.filter_by(id=prediction_id, user_id=current_user.id).first_or_404()
    top3 = json.loads(pred.top_3)
    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", f"prediction_{prediction_id}.pdf")
    create_prediction_report(path, current_user.name, current_user.email, pred.symptoms.split(", "), pred.predicted_disease, pred.confidence, top3, pred.explanation or "")
    return send_file(path, as_attachment=True)
