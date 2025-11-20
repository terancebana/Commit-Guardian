import urllib.request
import urllib.parse
import json
import config

def get_login_url():
    """
    Generates the URL where the user clicks 'Authorize'.
    """
    params = {
        "client_id": config.GITHUB_CLIENT_ID,
        "redirect_uri": f"{config.BASE_URL}/auth/callback",
        "scope": "repo read:user",
        "allow_signup": "true"
    }
    # Converts dict to string: client_id=123&scope=repo...
    query_string = urllib.parse.urlencode(params)
    return f"{config.AUTH_URL}?{query_string}"

def exchange_code_for_token(code):
    """
    Trades the temporary code for a real Access Token.
    """
    # 1. Prepare the secret payload
    data = {
        "client_id": config.GITHUB_CLIENT_ID,
        "client_secret": config.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": f"{config.BASE_URL}/auth/callback"
    }
    
    # 2. Encode data for POST request
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    
    # 3. Request JSON response (otherwise GitHub sends XML)
    headers = {"Accept": "application/json"}

    req = urllib.request.Request(
        config.TOKEN_URL, 
        data=encoded_data, 
        headers=headers, 
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                return response_data.get("access_token")
            return None
    except Exception as e:
        print(f"Token Exchange Failed: {e}")
        return None

def get_user_profile(token):
    """
    Uses the token to ask GitHub 'Who is this?'
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CommitGuardian"
    }
    
    req = urllib.request.Request(config.USER_URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
            return None
    except Exception as e:
        print(f"Profile Fetch Error: {e}")
        return None