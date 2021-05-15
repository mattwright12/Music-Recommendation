from flask import Flask
from flask import render_template, g
from flask import Blueprint
from recommend.auth import login_required
from flask import request
from werkzeug.security import generate_password_hash
from recommend.validate import *
from music_recommender.db import get_db





app = Flask(__name__)

bp = Blueprint("change_password", __name__, url_prefix="/change_password")


@bp.route('/')
def index():
    '''Returns the Change Password back'''
    return render_template('change_password.html', username=g.user["username"])


@bp.route("/", methods=("GET", "POST"))
def change_password():
    '''Changes the user's password as a response to the submitting of an HTML form'''
    if request.method == "POST":
        password = request.form["password"]
        password_verification = request.form["password_verification"]
        error = []

        if not password:
            error.append("Password is required")
        if not validate_password(password):
            error.append('That password is invalid')
            password = ''
        if is_common_password(password):
            error.append('That password is too common')
            password = ''
        if password != password_verification:
            error.append("Those passwords don't match")
        if error == []:
            # the name is available, store it in the database and go to
            # the login page
            db = get_db()
            db.execute("UPDATE user SET password=? WHERE username=?", (generate_password_hash(password), g.user["username"]),)
            db.commit()
            return render_template('my_profile.html', username=g.user["username"])
        else:
            return  render_template('change_password.html', error=';'.join(error))
