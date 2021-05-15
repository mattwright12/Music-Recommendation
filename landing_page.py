
from flask import Blueprint
from flask import render_template

bp = Blueprint("landing", __name__)


@bp.route("/")
def index():
    '''Returns the HTML of the landing page of the site'''
    return render_template('landing_page.html')
