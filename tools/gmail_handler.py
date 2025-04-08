import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from gmail.gmail_auth import get_gmail_service  # Make sure this exists

def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_reply(to, subject, message_text):
    service = get_gmail_service()
    if not service:
        print("[ERROR] Gmail service not initialized. Cannot send email.")
        return None
    message = create_message(to, subject, message_text)
    try:
        sent = service.users().messages().send(userId='me', body=message).execute()
        print(f"Message sent to {to} with ID: {sent['id']}")
        return sent
    except Exception as e:
        print(f"[ERROR] An error occurred while sending email: {e}")
        return None

def send_email(to, subject, message_text):
    """A more general function to send emails."""
    service = get_gmail_service()
    if not service:
        print("[ERROR] Gmail service not initialized. Cannot send email.")
        return None
    message = create_message(to, subject, message_text)
    try:
        sent = service.users().messages().send(userId='me', body=message).execute()
        print(f"Email sent to {to} with ID: {sent['id']}")
        return sent
    except Exception as e:
        print(f"[ERROR] An error occurred while sending email: {e}")
        return None