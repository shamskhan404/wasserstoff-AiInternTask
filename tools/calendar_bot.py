import os
from datetime import datetime, timedelta
import json

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("Google API libraries not found. Install via: pip install google-api-python-client google-auth")

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")  # Path to your credentials .json
TIMEZONE = 'Asia/Kolkata' 

def create_calendar_event(event_data):
    """
    event_data: dict with keys ['summary', 'start_time', 'end_time', 'location']
    start_time and end_time should be in ISO format (YYYY-MM-DDTHH:MM:SS).
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build("calendar", "v3", credentials=credentials)

        event = {
            'summary': event_data.get('summary', 'Meeting'),
            'description': event_data.get('description', ''),
            'start': {
                'dateTime': event_data['start_time'],
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': event_data['end_time'],
                'timeZone': TIMEZONE,
            },
            'location': event_data.get('location', ''),
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event.get('htmlLink')

    except Exception as e:
        print("Google Calendar API call failed:", e)
        return None

def create_dummy_calendar_event(event_data):
    print(f"[DUMMY CALENDAR EVENT CREATED]: {event_data}")
    return "Dummy calendar event created."