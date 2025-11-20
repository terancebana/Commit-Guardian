import uuid
import http.cookies
import http.server
import socketserver
import json
import os
import urllib.parse
import github_client
import junk_pusher
import database
import auth  # <--- New Import

SESSIONS = {}
PORT = 8000
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

class CommitGuardianHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. The Login Route (User clicks "Login")
        if self.path == '/login':
            self.handle_login()
            return

        # 2. The Callback Route (GitHub sends user back here)
        if self.path.startswith('/auth/callback'):
            self.handle_callback()
            return

        # 3. The API Routes
        if self.path == '/api/status':
            self.handle_api_status()
        else:
            # 4. Serving Files (HTML/CSS/JS)
            self.handle_static_files()

    def do_POST(self):
        if self.path == '/api/push-junk':
            # 1. Check Session (Security)
            if "Cookie" not in self.headers:
                self.send_error(401, "Not authenticated")
                return

            cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
            if "session_id" not in cookie:
                self.send_error(401, "No session found")
                return

            session_id = cookie["session_id"].value
            user_data = SESSIONS.get(session_id)

            if not user_data:
                self.send_error(401, "Invalid session")
                return

            # 2. Call Pusher with Logged-in Data
            success = junk_pusher.push_junk_commit(
                user_data['username'],
                user_data['token']
            )
            
            if success:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status": "pushed"}')
            else:
                self.send_error(500, "Failed to push (Check logs/permissions)")
        else:
            self.send_error(404, "Not Found")

    # --- NEW AUTH HANDLERS ---

    def handle_login(self):
        # Get the GitHub link from our auth.py script
        login_url = auth.get_login_url()
        
        print(f"DEBUG: Redirecting to -> {login_url}")

        # Send a 302 Redirect (Standard way to send a browser somewhere else)
        self.send_response(302)
        self.send_header('Location', login_url)
        self.end_headers()

    def handle_callback(self):
        # 1. Parse code
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = query_components.get('code', [None])[0]

        if not code:
            self.send_error(400, "No code provided")
            return

        # 2. Exchange code for Token
        token = auth.exchange_code_for_token(code)
        if not token:
            self.send_error(500, "Failed to exchange token")
            return

        # 3. Get User Profile
        user_profile = auth.get_user_profile(token)
        if not user_profile:
            self.send_error(500, "Failed to fetch profile")
            return

        username = user_profile.get('login')
        email = user_profile.get('email')

        database.save_user(username, token, email)
        # --- NEW: CREATE SESSION ---
        # Generate a random ID (The "Wristband")
        session_id = str(uuid.uuid4())
        
        # Save user info in our memory
        SESSIONS[session_id] = {
            "token": token,
            "username": user_profile.get('login')
        }
        
        # 4. Redirect to Dashboard with Cookie
        self.send_response(302)
        self.send_header('Location', '/')
        # This sets the cookie in the browser
        self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')
        self.end_headers()

    def handle_api_status(self):
        # 1. Check for Cookie
        if "Cookie" not in self.headers:
            self._send_json(401, {"error": "not_authenticated", "pushed_today": False})
            return

        # 2. Parse Cookie
        cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
        if "session_id" not in cookie:
            self._send_json(401, {"error": "no_session", "pushed_today": False})
            return

        session_id = cookie["session_id"].value
        
        # 3. Look up user in our memory
        user_data = SESSIONS.get(session_id)
        
        if not user_data:
            self._send_json(401, {"error": "invalid_session", "pushed_today": False})
            return

        # 4. Fetch Real GitHub Data using the logged-in user's token
        try:
            data = github_client.get_activity_status(
                user_data['username'], 
                user_data['token']
            )
            self._send_json(200, data)
        except Exception as e:
            self.send_error(500, str(e))

    # Helper to save lines of code
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def handle_static_files(self):
        if self.path == '/':
            self.path = '/index.html'
        
        clean_path = self.path.lstrip('/')
        file_path = os.path.join(FRONTEND_DIR, clean_path)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            if file_path.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif file_path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif file_path.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

if __name__ == "__main__":
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with ReusableTCPServer(("", PORT), CommitGuardianHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.server_close()