"""Application entrypoint: configures Flask extensions and registers blueprints."""
import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy import text

from model import db, User
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp


login_manager = LoginManager()
mail = Mail()


def create_app():
    """Creates and configures the Flask application instance."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")
    app.config["MAIL_SUPPRESS_SEND"] = os.getenv("MAIL_SUPPRESS_SEND", "true").lower() == "true"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "user.login"
    mail.init_app(app)

    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    register_error_handlers(app)

    with app.app_context():
        db.create_all()
        ensure_schema_compatibility()
        ensure_default_admin()

    return app


def register_error_handlers(app: Flask):
    """Registers application-level custom error pages."""
    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_):
        return render_template("errors/500.html"), 500


def ensure_schema_compatibility():
    """Adds missing columns for sqlite upgrades without dropping existing data."""
    if "sqlite" not in str(db.engine.url):
        return

    conn = db.session.connection()
    columns = {row[1] for row in conn.execute(text("PRAGMA table_info(user)")).fetchall()}
    if "username" not in columns:
        conn.execute(text("ALTER TABLE user ADD COLUMN username VARCHAR(80)"))
        conn.execute(text("UPDATE user SET username = lower(replace(name, ' ', '')) || id WHERE username IS NULL"))
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    """Loads a user by id for Flask-Login session management."""
    return User.query.get(int(user_id))


def ensure_default_admin():
    """Creates a default admin account if one does not already exist."""
    admin = User.query.filter_by(email="admin@health.local").first()
    if not admin:
        admin = User(name="System Admin", username="admin", email="admin@health.local", role="Admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
    elif not admin.username:
        admin.username = "admin"
        db.session.commit()


app = create_app()
app.extensions["mail"] = mail


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
