from flask import (
    Blueprint, render_template, request
)

bp = Blueprint('home', __name__)


@bp.route('/')
def home():
    return render_template('home/home.html')
