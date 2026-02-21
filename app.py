"""Application entrypoint: configures Flask extensions and registers blueprints."""
import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail

from model import db, User
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp


login_manager = LoginManager()
mail = Mail()


def create_app():
    """Creates and configures the Flask application instance."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")
    app.config["MAIL_SUPPRESS_SEND"] = True

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "user.login"
    mail.init_app(app)

    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        ensure_default_admin()

    return app


@login_manager.user_loader
def load_user(user_id):
    """Loads a user by id for Flask-Login session management."""
    return User.query.get(int(user_id))


def ensure_default_admin():
    """Creates a default admin account if one does not already exist."""
    admin = User.query.filter_by(email="admin@health.local").first()
    if not admin:
        admin = User(name="System Admin", email="admin@health.local", role="Admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()


app = create_app()
app.extensions["mail"] = mail


if __name__ == "__main__":
    app.run(debug=True)
