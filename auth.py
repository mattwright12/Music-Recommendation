import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from recommend.validate import *

from music_recommender.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_verification = request.form["password_verification"]
        email = request.form['email']
        db = get_db()
        error = []

        if not username:
            error.append("Username is required")
        if not password:
            error.append("Password is required")
        if not email:
            error.append('An email is required')
        if not validate_password(password):
            error.append('That password is invalid')
            password = ''
        if not validate_username(username):
            error.append('That username is invalid')
            username = ''
        if not validate_email(email):
            if not ("An email is required. " in error):
                error.append('That email is invalid')
            email = ''
        if is_common_password(password):
            error.append('That password is too common')
            password = ''
        if password != password_verification:
            error.append("Those passwords don't match")
        if (
            db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            is not None
        ):
            error.append(f"User {username} is already registered")
            username = ''

        if (
            db.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
            is not None
        ):
            error.append(f"That email is already registered")
            email = ''

        if error==[]:
            # the name is available, store it in the database and go to
            # the login page
            db.execute(
                "INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), email),
            )
            db.commit()
            return redirect(url_for("auth.login"))

        #flash(error)

        error_message = ''


        for i in range(len(error)):
            error_message += error[i]
            if i != len(error)-1:
                error_message += '; '

        error_message += '.'


        return render_template("auth/register.html", error=error_message, password=password, username=username)
    return render_template("auth/register.html", error=None, password='', username='')


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
            username = ''
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
            password = ''

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("add_tastes"))

        #flash(error)

        return render_template("auth/login.html", error=error, password=password, username=username)
    return render_template("auth/login.html", error=None, password='', username='')

@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("add_tastes"))




