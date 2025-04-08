from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import Config
import os

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://mail.google.com/'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print('Please run the Gmail API quickstart script to generate token.json.')
            print('It typically involves steps like downloading credentials.json from Google Cloud.')
            print('Then, run a script that uses the google-auth-oauthlib library to authenticate.')
            print('This project is set up to use a refresh token from your .env file for non-interactive use.')
            if Config.GMAIL_REFRESH_TOKEN and Config.GMAIL_CLIENT_ID and Config.GMAIL_CLIENT_SECRET:
                creds = Credentials(
                    token=None, 
                    refresh_token=Config.GMAIL_REFRESH_TOKEN,
                    client_id=Config.GMAIL_CLIENT_ID,
                    client_secret=Config.GMAIL_CLIENT_SECRET,
                    token_uri="https://oauth2.googleapis.com/token",
                    scopes=['https://mail.google.com/']
                )
                creds.refresh(Request())
            else:
                print("[ERROR] Gmail refresh token, client ID, or client secret not found in .env.")
                return None

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"[ERROR] Could not build Gmail service: {e}")
        return None