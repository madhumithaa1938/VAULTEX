
import logging

from flask import Flask, render_template, request
from flask_login import login_required, current_user

from config import Config
from extensions import login_manager, csrf
from models import User

from database.database import (
    initialize_database,
    get_user_by_id,
    get_files_by_user
)

from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.download import download_bp


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    if (
        not app.config.get("SECRET_KEY")
        or app.config["SECRET_KEY"].startswith("REPLACE_")
    ):
        raise RuntimeError(
            "Set a real FLASK_SECRET_KEY in your private .env file."
        )

    logging.basicConfig(level=logging.INFO, force=True)
    app.logger.setLevel(logging.INFO)

    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            row = get_user_by_id(int(user_id))

            if row is None:
                return None

            return User(
                row["id"],
                row["username"],
                row["email"],
                row["password_hash"]
            )

        except (ValueError, TypeError):
            return None

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(download_bp)

    with app.app_context():
        initialize_database()

    # Diagnostic: print every request received by Flask.
    @app.before_request
    def log_incoming_request():
        user_status = (
            f"user_id={current_user.id}"
            if current_user.is_authenticated
            else "not_logged_in"
        )

        print(
            f"[VAULTEX REQUEST] {request.method} "
            f"{request.path} | {user_status}",
            flush=True
        )

    # Diagnostic: print the response status.
    @app.after_request
    def log_outgoing_response(response):
        print(
            f"[VAULTEX RESPONSE] {request.method} "
            f"{request.path} | HTTP {response.status_code}",
            flush=True
        )
        return response

    @app.route("/")
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/files")
    @login_required
    def files_page():
        return render_template(
            "files.html",
            files=get_files_by_user(int(current_user.id))
        )

    @app.route("/security")
    @login_required
    def security_page():
        return render_template("security.html")

    @app.route("/settings")
    @login_required
    def settings_page():
        return render_template("settings.html")

    return app


app = create_app()


if __name__ == "__main__":
    print("VAULTEX DIAGNOSTIC SERVER STARTING", flush=True)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
