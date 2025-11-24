import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_alert(target_email, username):
    # 1. Check if email exists
    if not target_email:
        print(f"Error: No email address for user {username}")
        return False

    sender = config.EMAIL_SENDER
    password = config.EMAIL_PASSWORD

    # 2. Check if server credentials exist
    if not sender or not password:
        print("Error: Server email credentials missing in config.")
        return False

    # 3. Create the Email
    subject = "Action Required: Github Streak Risk"
    
    # HTML Body (The pretty part)
    body = f"""
    <html>
      <body>
        <h2 style="color: #d9534f;">Commit Guardian Alert</h2>
        <p>Hi <strong>{username}</strong>,</p>
        <p>We noticed you haven't pushed any code to GitHub today!</p>
        <p>Your daily streak is at risk.</p>
        <br>
        <a href="{config.BASE_URL}" style="padding: 12px 24px; background-color: #d9534f; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
            Go to Dashboard to Fix
        </a>
        <br><br>
        <p style="font-size: 12px; color: gray;">This is an automated message from your CommitGuardian server.</p>
      </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = target_email
    message.attach(MIMEText(body, "html"))

    # 4. Send via Gmail SMTP (Standard Library)
    try:
        context = ssl.create_default_context()
        # Connect to Gmail's secure port 465
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, target_email, message.as_string())
        
        print(f"DEBUG: Alert sent successfully to {target_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
