from flask import Flask
from flask import render_template, g
from flask import Blueprint
from recommend.auth import login_required
from flask import request
from werkzeug.security import generate_password_hash
from recommend.validate import *
from music_recommender.db import get_db





app = Flask(__name__)

bp = Blueprint("my_profile", __name__, url_prefix="/my_profile")

@bp.route('/')
@login_required
def index():
    '''Renders the initial My Profile page'''
    return render_template('my_profile.html', username=g.user["username"])

