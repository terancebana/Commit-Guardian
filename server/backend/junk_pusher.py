import urllib.request
import json
import base64
import datetime
import config

def push_junk_commit(username, token):
    repo = config.JUNK_REPO_NAME
    filename = "daily_log.txt"
    
    url = f"https://api.github.com/repos/{username}/{repo}/contents/{filename}"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CommitGuardian"
    }

    file_sha = None
    try:
        req_get = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req_get) as response:
            data = json.loads(response.read().decode())
            file_sha = data.get('sha')
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return False

    timestamp = datetime.datetime.now().isoformat()
    new_content = f"Streak kept alive at: {timestamp}\n"
    encoded_content = base64.b64encode(new_content.encode()).decode()

    data = {
        "message": f"Automated commit {timestamp}",
        "content": encoded_content
    }
    if file_sha:
        data["sha"] = file_sha

    json_data = json.dumps(data).encode('utf-8')
    req_put = urllib.request.Request(url, data=json_data, headers=headers, method='PUT')

    try:
        with urllib.request.urlopen(req_put) as response:
            if response.status in [200, 201]:
                return True
    except Exception:
        return False

    return False