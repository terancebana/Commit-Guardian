import json
import os

# Define where the database file lives
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "data", "users.json")

def load_users():
    """Reads the JSON file and returns a dictionary of users."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return {}

def save_user(username, token, email=None):
    """Updates or adds a user to the database."""
    users = load_users()
    
    # Update the user's info
    users[username] = {
        "token": token,
        "email": email,
        "active": True
    }
    
    # Write back to disk
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(users, f, indent=4)
        print(f"DEBUG: User {username} saved to database.")
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False