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
        if self.path.startswith('/login'):
            if self.path == '/login' or self.path.startswith('/login?'):
                self.handle_login()
                return
        if self.path.startswith('/auth/callback'):
            self.handle_callback()
            return
        if self.path == '/api/status':
            self.handle_api_status()
            return
        if self.path == '/login.html':
            self.handle_static_files()
            return
        if self.path == '/':
            self.handle_static_files()
            return
        self.handle_static_files()

    def do_POST(self):
        if self.path == '/api/push-junk':
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
            return
        if self.path == '/logout':
            self._handle_logout()
            return
        if self.path == '/api/simulate-miss':
            if "Cookie" not in self.headers:
                self._send_json(401, {"error": "not_authenticated"})
                return
            cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
            if "session_id" not in cookie:
                self._send_json(401, {"error": "no_session"})
                return
            session_id = cookie["session_id"].value
            user_data = SESSIONS.get(session_id)
            if not user_data:
                self._send_json(401, {"error": "invalid_session"})
                return
            user_data['simulate_miss'] = True
            self._send_json(200, {"simulate_miss": True})
            return
        if self.path == '/api/clear-simulate':
            if "Cookie" not in self.headers:
                self._send_json(401, {"error": "not_authenticated"})
                return
            cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
            if "session_id" not in cookie:
                self._send_json(401, {"error": "no_session"})
                return
            session_id = cookie["session_id"].value
            user_data = SESSIONS.get(session_id)
            if not user_data:
                self._send_json(401, {"error": "invalid_session"})
                return
            user_data['simulate_miss'] = False
            self._send_json(200, {"simulate_miss": False})
            return
        if self.path == '/api/send-test-email':
            if "Cookie" not in self.headers:
                self._send_json(401, {"error": "not_authenticated"})
                return
            cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
            if "session_id" not in cookie:
                self._send_json(401, {"error": "no_session"})
                return
            session_id = cookie["session_id"].value
            user_data = SESSIONS.get(session_id)
            if not user_data:
                self._send_json(401, {"error": "invalid_session"})
                return
            users = database.load_users()
            username = user_data.get('username')
            user_record = users.get(username, {})
            target_email = user_record.get('email')
            try:
                import notifier
                success = notifier.send_alert(target_email, username)
                if success:
                    self._send_json(200, {"sent": True})
                else:
                    self._send_json(500, {"sent": False})
            except Exception:
                self._send_json(500, {"sent": False})
            return
        self.send_error(404, "Not Found")

    def do_GET(self):
        if self.path.startswith('/login'):
            if self.path == '/login' or self.path.startswith('/login?'):
                self.handle_login()
                return
        if self.path.startswith('/auth/callback'):
            self.handle_callback()
            return
        if self.path == '/api/status':
            self.handle_api_status()
            return
        if self.path == '/logout':
            self._handle_logout()
            return
        if self.path == '/login.html':
            self.handle_static_files()
            return
        if self.path == '/':
            self.handle_static_files()
            return
        self.handle_static_files()

    def _handle_logout(self):
        if "Cookie" in self.headers:
            cookie = http.cookies.SimpleCookie(self.headers["Cookie"])
            if "session_id" in cookie:
                session_id = cookie["session_id"].value
                SESSIONS.pop(session_id, None)
        self.send_response(200)
        self.send_header('Set-Cookie', 'session_id=deleted; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
        self.end_headers()
        self.wfile.write(b'{}')

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
        if not email:
            emails = auth.get_user_emails(token)
            primary = None
            for e in emails:
                if e.get('primary') and e.get('verified'):
                    primary = e.get('email')
                    break
            if not primary:
                for e in emails:
                    if e.get('verified'):
                        primary = e.get('email')
                        break
            email = primary

        database.save_user(username, token, email)
        session_id = str(uuid.uuid4())
        
        # Save user info in our memory
        SESSIONS[session_id] = {
            "token": token,
            "username": user_profile.get('login'),
            "simulate_miss": False
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
            if user_data.get('simulate_miss'):
                if data.get('pushed_today'):
                    data['current_streak'] = max(0, data.get('current_streak', 0) - 1)
                data['pushed_today'] = False
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