"""Admin routes for user and dataset management."""
import os
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from model import db, User, Prediction, DatasetMeta
from routes.user_routes import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@role_required("Admin")
def admin_dashboard():
    """Shows global system statistics for administrators."""
    total_users = User.query.count()
    total_predictions = Prediction.query.count()
    latest = Prediction.query.order_by(Prediction.timestamp.desc()).first()
    latest_acc = latest.confidence if latest else 0
    return render_template("admin/admin_dashboard.html", total_users=total_users, total_predictions=total_predictions, latest_acc=latest_acc)


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def users():
    """Allows admin to view, create, and delete users."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "Patient")
        if not all([name, email, password]):
            flash("All fields are required.", "warning")
            return redirect(url_for("admin.users"))
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("User added.", "success")
        return redirect(url_for("admin.users"))

    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/delete/<int:user_id>")
@login_required
@role_required("Admin")
def delete_user(user_id):
    """Deletes a user account except for the currently logged-in admin account."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "warning")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/dataset", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def dataset():
    """Displays dataset metadata and allows replacing the dataset CSV file."""
    dataset_path = "dataset/disease_symptoms.csv"
    if request.method == "POST":
        uploaded = request.files.get("dataset_file")
        if uploaded and uploaded.filename.endswith(".csv"):
            uploaded.save(dataset_path)
            df = pd.read_csv(dataset_path)
            meta = DatasetMeta(file_name=uploaded.filename, rows=len(df))
            db.session.add(meta)
            db.session.commit()
            flash("Dataset updated. Please retrain model.", "success")
        else:
            flash("Please upload a valid CSV file.", "danger")
        return redirect(url_for("admin.dataset"))

    info = {"exists": os.path.exists(dataset_path), "rows": 0, "columns": []}
    if info["exists"]:
        df = pd.read_csv(dataset_path)
        info["rows"] = len(df)
        info["columns"] = list(df.columns)

    history = DatasetMeta.query.order_by(DatasetMeta.uploaded_at.desc()).all()
    return render_template("admin/dataset.html", info=info, history=history)
