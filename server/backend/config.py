import os

def load_env(filepath='../data/.env'):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)

    print(f"DEBUG: Loading env from {full_path}")

    try:
        with open(full_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments or empty lines
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    
                    # Set the variable
                    os.environ[key] = value
                    print(f"DEBUG: Loaded key -> {key}") # Confirms the key was read
                    
    except FileNotFoundError:
        print("DEBUG: .env file not found")
        pass

load_env()

# Load variables
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')
JUNK_REPO_NAME = os.getenv('JUNK_REPO_NAME', 'daily-activity-log')

# URLs
AUTH_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"
USER_URL = "https://api.github.com/user"

# Email Configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')