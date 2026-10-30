
import re
import sqlite3

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.database import (
    create_user,
    get_user_by_email
)

from models import User


auth_bp = Blueprint("auth", __name__)


def validate_email(email):

    return bool(
        email
        and len(email) <= 254
        and re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        )
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        if not 3 <= len(username) <= 50:

            flash(
                "Username must contain 3 to 50 characters.",
                "error"
            )

        elif not validate_email(email):

            flash(
                "Enter a valid email address.",
                "error"
            )

        elif not 12 <= len(password) <= 128:

            flash(
                "Password must contain 12 to 128 characters.",
                "error"
            )

        else:

            try:

                create_user(
                    username,
                    email,
                    generate_password_hash(password)
                )

                flash(
                    "Account created. Please sign in.",
                    "success"
                )

                return redirect(
                    url_for("auth.login")
                )

            except sqlite3.IntegrityError:

                flash(
                    "That username or email is already registered.",
                    "error"
                )

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        user_data = (
            get_user_by_email(email)
            if validate_email(email)
            and len(password) <= 128
            else None
        )

        if (
            user_data
            and check_password_hash(
                user_data["password_hash"],
                password
            )
        ):

            user = User(
                user_data["id"],
                user_data["username"],
                user_data["email"],
                user_data["password_hash"]
            )

            login_user(user, fresh=True)

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash(
        "You have signed out.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )
