import urllib.request
import json
from datetime import datetime, timedelta, timezone
import config

# UPDATED: Now accepts username and token as arguments
def get_user_events(username, token):
    if not username or not token:
        print("Error: Missing username or token")
        return []

    url = f"https://api.github.com/users/{username}/events?per_page=100"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CommitGuardian"
    }

    request = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
            return []
    except Exception as e:
        print(f"Connection error: {e}")
        return []

# UPDATED: Now accepts username and token
def get_activity_status(username, token):
    events = get_user_events(username, token)
    
    # ... (The rest of the logic stays exactly the same) ...
    
    push_dates = set()
    for event in events:
        if event['type'] == 'PushEvent':
            date_str = event['created_at'].split('T')[0]
            push_dates.add(date_str)
            
    now = datetime.now(timezone.utc)
    today_str = now.strftime('%Y-%m-%d')
    
    pushed_today = today_str in push_dates
    
    streak = 0
    check_date = now
    
    if not pushed_today:
        check_date = now - timedelta(days=1)
        
    while True:
        check_str = check_date.strftime('%Y-%m-%d')
        if check_str in push_dates:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
            
    return {
        "pushed_today": pushed_today,
        "current_streak": streak,
        "last_push_date": max(push_dates) if push_dates else None
    }