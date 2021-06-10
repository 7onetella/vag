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
import traceback


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


def secure_url_for(route_name: str) -> str:
    return url_for(route_name, _external=True, _scheme="https")


@app.route("/")
def index():
    return render_template('home.html', profile=profile, logged_in=False)


@app.route("/main")
def main():
    logger.info("main")
    if current_user.is_authenticated:
        logger.info(current_user)
    else:
        return redirect(secure_url_for("login"))

    profile = get_build_profile(current_user.name, 'vscode')
    return render_template('main.html', profile=profile, logged_in=True)


@app.route('/profile/')
@login_required
def profile():
    profile = get_build_profile(current_user.name, 'vscode')
    return render_template('profile.html', profile=profile, logged_in=True)


def get_google_request_uri() -> str:
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return request_uri


@app.route("/login")
def login():
    return redirect(get_google_request_uri())  


@app.route("/signup")
def signup():
    return redirect(get_google_request_uri())  


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/signup/callback")
def signup_callback():
    logger.info("/signup/callback")

    userinfo_response = get_userinfo_response()

    if userinfo_response.json().get("email_verified"):
        userinfo_json = userinfo_response.json()

        if args.debug: 
            logger.info(userinfo_json)

        google_id = userinfo_json["sub"]
        users_email = userinfo_json["email"]
        picture = userinfo_json["picture"]
        firstname = userinfo_json["given_name"]
        lastname = userinfo_json["family_name"]

        try:
            db_user = find_user_by_google_id(google_id)
            if db_user:
                logger.info("user found logging user in")
                user = UserObj(db_user.id, db_user.username, db_user.email)
                login_user(user)
            else:
                logger.info("user not found adding user to the databse")
                new_user = user_util.add_user(f'{firstname}{lastname}', 'teachmecoding', users_email, google_id, exitOnFailure=False)
                user = UserObj(google_id, new_user.username, new_user.email)
                login_user(user) 
                return redirect(secure_url_for("main")) 
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            tb = traceback.format_exc()
            logger.warning(f'{exc_type}, {fname}, {exc_tb.tb_lineno}, {tb}')

        logger.info('retrieving user done') 

        return redirect(secure_url_for("main"))
    else:
        return "User email not available or not verified by Google.", 400


def get_userinfo_response():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    token_response_json=json.dumps(token_response.json())
    if args.debug:
        logger.info(f'token_response_json={token_response_json}')

    client.parse_request_body_response(token_response_json)

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    return requests.get(uri, headers=headers, data=body)    


@app.route("/login/callback")
def callback():
    logger.info("/login/callback")

    userinfo_response = get_userinfo_response()

    if userinfo_response.json().get("email_verified"):
        userinfo_json = userinfo_response.json()

        if args.debug: 
            logger.info(userinfo_json)

        google_id = userinfo_json["sub"]
        users_email = userinfo_json["email"]
        picture = userinfo_json["picture"]
        firstname = userinfo_json["given_name"]
        lastname = userinfo_json["family_name"]

        try:
            db_user = find_user_by_google_id(google_id)
            if db_user:
                user = UserObj(google_id, db_user.username, db_user.email)
                login_user(user)
            else:
                return redirect(secure_url_for("sign_up_needed")) 
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.warning(f'{exc_type}, {fname}, {exc_tb.tb_lineno}')

        logger.info('retrieving user done') 

        # https://github.com/pallets/flask/issues/773  redirect not aware of https
        return redirect(secure_url_for("main"))
    else:
        return "User email not available or not verified by Google.", 400


@app.route("/sign_up_needed")
def sign_up_needed():
    return render_template('sign_up_needed.html')    


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(secure_url_for("logged_out"))


@app.route("/logged_out")
def logged_out():
    return render_template('logged_out.html')


@login_manager.user_loader
def load_user(google_id: str):
    print(f"load_user {google_id}")
    u = find_user_by_google_id(google_id)
    return UserObj(u.id, u.username, u.email)


@app.route("/health")
def health():
    return "OK" 


if __name__ == "__main__":
    if args.debug:
        app.run(debug=True, ssl_context="adhoc")
    else:
        app.run(debug=False, host='0.0.0.0', port=5000)

