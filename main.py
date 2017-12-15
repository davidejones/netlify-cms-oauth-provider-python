from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect
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
token_url = '{token_host}{token_path}'.format(token_host=token_host, token_path=token_path)
scope = os.environ.get('SCOPES', 'repo,user')
ssl_enabled = os.environ.get('SSL_ENABLED', '0') == '1'


@app.route("/")
def index():
    """ Show a log in with github link """
    return 'Hello<br><a href="/auth">Log in with Github</a>'


@app.route("/auth")
def auth():
    """ We clicked login now redirect to github auth """
    github = OAuth2Session(client_id, scope=scope)
    authorization_url, state = github.authorization_url(authorization_base_url)
    return redirect(authorization_url)


@app.route("/callback", methods=["GET"])
def callback():
    """ retrieve access token """
    state = request.args.get('state', '')
    try:
        github = OAuth2Session(client_id, state=state, scope=scope)
        token = github.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
        content = json.dumps({'token': token.get('access_token', ''), 'provider': 'github'})
        message = 'success'
    except BaseException as e:
        message = 'error'
        content = str(e)
    post_message = json.dumps('authorization:github:{0}:{1}'.format(message, content))
    return """<html><body><script>
    (function() {
      function recieveMessage(e) {
        console.log("recieveMessage %o", e)
        // send message to main window with da app
        window.opener.postMessage(
          """+post_message+""",
          e.origin
        )
      }
      window.addEventListener("message", recieveMessage, false)
      // Start handshare with parent
      console.log("Sending message: %o", "github")
      window.opener.postMessage("authorizing:github", "*")
      })()
    </script></body></html>"""


@app.route("/success", methods=["GET"])
def success():
    return '', 204


if __name__ == "__main__":
    run_config = {}
    if not ssl_enabled:
        # allows us to use a plain HTTP callback
        os.environ['DEBUG'] = "1"
        # If your server is not parametrized to allow HTTPS set this
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    else:
        run_config = {'ssl_context': 'adhoc'}
    app.secret_key = os.urandom(24)
    app.run(port=3000, debug=True, **run_config)
