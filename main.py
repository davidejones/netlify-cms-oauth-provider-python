from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv(join(dirname(__file__), '.env'))
client_id = os.environ.get("OAUTH_CLIENT_ID")
client_secret = os.environ.get("OAUTH_CLIENT_SECRET")
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_host = os.environ.get('GIT_HOSTNAME', 'https://github.com')
token_path = os.environ.get('OAUTH_TOKEN_PATH', '/login/oauth/access_token')
authorize_path = os.environ.get('OAUTH_AUTHORIZE_PATH', '/login/oauth/authorize')
token_url = '{token_host}{authorize_path}'.format(token_host=token_host, authorize_path=authorize_path)


@app.route("/")
def index():
    """ Show a log in with github link """
    return 'Hello<br><a href="/auth">Log in with Github</a>'


@app.route("/auth")
def auth():
    """ We clicked login now redirect to github auth """
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route("/callback", methods=["GET"])
def callback():
    """ retrieve access token """
    try:
        github = OAuth2Session(client_id, state=session['oauth_state'])
        token = github.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
        session['oauth_token'] = token
        content = json.dumps({'token': token, 'provider': 'github'})
        message = 'success'
    except BaseException as e:
        message = 'error'
        content = str(e)
    script = """<script>
    (function() {
      function recieveMessage(e) {
        console.log("recieveMessage %o", e)
        // send message to main window with da app
        window.opener.postMessage(
          'authorization:github:{message}:{content}',
          e.origin
        )
      }
      window.addEventListener("message", recieveMessage, false)
      // Start handshare with parent
      console.log("Sending message: %o", "github")
      window.opener.postMessage("authorizing:github", "*")
      })()
    </script>"""
    return script.format(message=message, content=content)


@app.route("/success", methods=["GET"])
def success():
    return '', 204


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"
    app.secret_key = os.urandom(24)
    app.run(debug=True)
