from flask import Flask
from markupsafe import escape
from flask import render_template
from vag.utils.cx_db_util import *


app = Flask(__name__)

@app.route("/")
def index():
    profile = get_build_profile('mo', 'vscode')
    return render_template('main.html', profile=profile)

@app.route('/profile/')
def hello(name=None):
    profile = get_build_profile('mo', 'vscode')
    return render_template('profile.html', profile=profile)