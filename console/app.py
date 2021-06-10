from vag.utils import user_util
from flask import Flask
from markupsafe import escape
from flask import render_template
from vag.utils.cx_db_util import *
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
import argparse
import logging


logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="debug mode")
args = parser.parse_args()


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
logger = logging.getLogger("app.py")  # or __name__ for current module
logger.setLevel(logging.INFO)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)


@app.route("/")
def index():
    logger.info("index")
    if current_user.is_authenticated:
        logger.info(current_user)
    else:
        return redirect(url_for("login", _external=True, _scheme="https"))

    profile = get_build_profile('mo', 'vscode')
    return render_template('main.html', profile=profile, logged_in=True)


@app.route('/profile/')
@login_required
def profile():
    profile = get_build_profile('mo', 'vscode')
    return render_template('profile.html', profile=profile, logged_in=True)


@app.route("/login")
def login():
    logger.info("/login")
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    redirect_uri = request.base_url + "/callback"
    redirect_uri = redirect_uri.replace('http://', 'https://') 
    logger.info(f'redirect_uri = {redirect_uri}')

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)  


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login/callback")
def callback():
    logger.info("/login/callback")
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    redirect_url = request.base_url.replace('http://', 'https://') 
    logger.info(f'redirect_url = {redirect_url}')
    
    request_url = request.url.replace('http://', 'https://')
    logger.info(f'request_url = {request_url}')

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request_url,
        redirect_url=redirect_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    token_response_json=json.dumps(token_response.json())
    logger.info(f'token_response_json={token_response_json}')

    client.parse_request_body_response(token_response_json)

    logger.info('parsing token response done') 

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        userinfo_json = userinfo_response.json()
        
        logger.info(userinfo_json)

        unique_id = userinfo_json["sub"]
        users_email = userinfo_json["email"]
        picture = userinfo_json["picture"]
        firstname = userinfo_json["given_name"]
        lastname = userinfo_json["family_name"]

        try:
            u = find_user_by_username('mo')
            user = UserObj(u.id, u.username, u.email)
            login_user(user)
        except:
            e = sys.exc_info()[0]
            logger.warning(e)

        logger.info('retrieving user done') 

        # new_user = user_util.add_user(users_name, 'teachmecoding', users_email, exitOnFailure=False)
        # if new_user:

        logger.info('logging in user done') 

        profile = get_build_profile('mo', 'vscode')
        # return render_template('main.html', profile=profile)
        # return render_template('user.html', unique_id=unique_id, users_email=users_email, picture=picture, users_name=users_name) 

        logger.info('logging in user done') 

        return redirect(url_for("index", _external=True, _scheme="https"))
    else:
        return "User email not available or not verified by Google.", 400


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("logged_out", _external=True, _scheme="https"))


@app.route("/logged_out")
def logged_out():
    return render_template('logged_out.html')


@login_manager.user_loader
def load_user(username: str):
    print(f"load_user {username}")
    u = find_user_by_username('mo')
    return UserObj(u.id, u.username, u.email)


@app.route("/health")
def health():
    return "OK" 


if __name__ == "__main__":
    if args.debug:
        app.run(debug=True, ssl_context="adhoc")
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)

