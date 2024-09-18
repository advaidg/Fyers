from flask import Flask, request, redirect, jsonify, render_template, url_for
from flask_cors import CORS
import requests
import random
import string
import hashlib

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

FYERS_LOGIN_URL = "https://api.fyers.in/api/v2/generate-authcode"  # Fyers login URL
app_id_hash = None


# Step 1: Render input form for client ID and secret ID
@app.route('/')
def index():
    return render_template('index.html')


# Step 2: Generate app ID hash and redirect to Fyers login
@app.route('/generate_token', methods=['POST'])
def generate_token():
    global app_id_hash
    client_id = request.form.get('client_id')
    secret_id = request.form.get('secret_id')

    if not client_id or not secret_id:
        return jsonify({"error": "Client ID and Secret ID are required"}), 400

    # Generate app ID hash
    app_id_hash = hashlib.sha256(f"{client_id}:{secret_id}".encode()).hexdigest()
    print(f"Generated app_id_hash: {app_id_hash}")  # Debugging output

    redirect_uri = "https://127.0.0.1:5001/callback"
    state = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))  # Random state value for security

    fyers_url = (
        f"{FYERS_LOGIN_URL}?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"state={state}&"
        f"app_id_hash={app_id_hash}"  # Pass the app_id_hash as a query parameter
    )

    return redirect(fyers_url)


# Step 3: Handle Fyers callback and get token
@app.route('/callback', methods=['GET'])
def callback():
    global app_id_hash
    auth_code = request.args.get('auth_code')

    if not auth_code:
        return jsonify({"error": "Missing auth_code"}), 400

    token_response = get_access_token(auth_code, app_id_hash)

    # If token is successfully received
    if 'access_token' in token_response:
        access_token = token_response['access_token']
        return redirect(url_for('success', token=access_token))  # Redirect to /success with token
    else:
        return jsonify({"error": "Failed to get token"})


# Success page to display the token
@app.route('/success/<token>')
def success(token):
    return render_template('success.html', token=token)


# Function to get access token from Fyers API using auth_code and app_id_hash
def get_access_token(auth_code, hash):
    access_token_url = "https://api-t1.fyers.in/api/v3/validate-authcode"
    payload = {
        'code': auth_code,
        'appIdHash': hash,
        'grant_type': "authorization_code"
    }

    try:
        response = requests.post(access_token_url, json=payload)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else {"error": response.text}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=5001)
