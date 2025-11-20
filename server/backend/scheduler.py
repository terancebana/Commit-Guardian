import database
import github_client
import notifier
import datetime

def run_checks():
    print(f"--- Running Daily Checks: {datetime.datetime.now()} ---")
    
    # 1. Load all users
    users = database.load_users()
    
    if not users:
        print("No users found in database.")
        return

    # 2. Check each user
    for username, data in users.items():
        token = data.get('token')
        email = data.get('email') # In a real app, ask user for email if missing
        
        # Temporary: If GitHub didn't give us an email (common), use your testing one
        # or skip. Ideally, you'd build a UI to ask the user for their email.
        if not email:
             print(f"Skipping {username}: No email on file.")
             continue

        print(f"Checking {username}...")
        
        try:
            # 3. Check Status using their specific token
            status = github_client.get_activity_status(username, token)
            
            if status['pushed_today']:
                print(f"  -> Safe (Streak: {status['current_streak']})")
            else:
                print(f"  -> DANGER! Sending alert to {email}...")
                success = notifier.send_alert(email, username)
                if success:
                    print("     Email sent.")
                else:
                    print("     Failed to send email.")
        except Exception as e:
            print(f"  -> Error checking {username}: {e}")

    print("--- Check Complete ---")

if __name__ == "__main__":
    run_checks()