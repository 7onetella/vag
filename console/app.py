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


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)


@app.route("/")
def index():
    print("index")
    if current_user.is_authenticated:
        print(current_user)
    else:
        return redirect(url_for("login"))

    profile = get_build_profile('mo', 'vscode')
    return render_template('main.html', profile=profile)


@app.route('/profile/')
def profile():
    profile = get_build_profile('mo', 'vscode')
    return render_template('profile.html', profile=profile)


@app.route("/login")
def login():
    print("/login")
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
    return redirect(request_uri)  


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login/callback")
def callback():
    print("/login/callback")
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
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        userinfo_json = userinfo_response.json()
        
        print(userinfo_json)

        unique_id = userinfo_json["sub"]
        users_email = userinfo_json["email"]
        picture = userinfo_json["picture"]
        firstname = userinfo_json["given_name"]
        lastname = userinfo_json["family_name"]

        u = find_user_by_username('mo')
        user = UserObj(u.id, u.username, u.email)

        # new_user = user_util.add_user(users_name, 'teachmecoding', users_email, exitOnFailure=False)
        # if new_user:
        login_user(user)

        profile = get_build_profile('mo', 'vscode')
        # return render_template('main.html', profile=profile)
        # return render_template('user.html', unique_id=unique_id, users_email=users_email, picture=picture, users_name=users_name) 
        return redirect(url_for("index"))
    else:
        return "User email not available or not verified by Google.", 400


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "You are logged out"


@login_manager.user_loader
def load_user(username: str):
    print(f"load_user {username}")
    u = find_user_by_username('mo')
    return UserObj(u.id, u.username, u.email)
    

if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")

