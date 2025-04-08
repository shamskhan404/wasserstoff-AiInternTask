# email_fetcher.py

import base64
from gmail.gmail_auth import get_gmail_service
from database.db_handler import store_email

def fetch_and_store_emails():
    """
    Fetch unread emails from Gmail, store in DB, and mark them as read.
    """
    service = get_gmail_service()

    try:
        results = (
            service.users()
                   .messages()
                   .list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=10)
                   .execute()
        )
        messages = results.get('messages', [])

        if not messages:
            print("No unread messages.")
            return

        print(f"Fetched {len(messages)} unread emails.")

        for msg in messages:
            msg_detail = (
                service.users()
                       .messages()
                       .get(userId='me', id=msg['id'], format='full')
                       .execute()
            )
            payload = msg_detail.get('payload', {})
            headers = payload.get('headers', [])
            parts   = payload.get('parts', [])

            email = {
                'id': msg['id'],
                'snippet': msg_detail.get('snippet', ''),
                'body': get_body_from_payload(payload),
                'subject': get_header(headers, 'Subject'),
                'sender': get_header(headers, 'From'),
                'recipient': get_header(headers, 'To'),
                'timestamp': get_header(headers, 'Date'),
                'in_reply_to': get_header(headers, 'In-Reply-To'),
                'thread_id': msg_detail.get('threadId'),
                'has_attachment': has_attachments(parts)
            }

            store_email(email)

            # Mark as read in Gmail
            service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

    except Exception as e:
        print(f"Error fetching/storing emails: {e}")


def decode_base64(data):
    try:
        return base64.urlsafe_b64decode(data.encode('UTF-8')).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"[decode_base64 error]: {e}")
        return ''

def get_body_from_payload(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part.get('body', {}):
                return decode_base64(part['body']['data'])
            elif part['mimeType'] == 'multipart/alternative':
                for sub in part.get('parts', []):
                    if sub['mimeType'] == 'text/plain' and 'data' in sub.get('body', {}):
                        return decode_base64(sub['body']['data'])
    elif payload.get('mimeType') == 'text/plain' and 'data' in payload.get('body', {}):
        return decode_base64(payload['body']['data'])
    return ''

def get_header(headers, name):
    for h in headers:
        if h['name'].lower() == name.lower():
            return h['value']
    return ''

def has_attachments(parts):
    for p in parts or []:
        if p.get('filename'):
            return True
        if p.get('parts') and has_attachments(p['parts']):
            return True
    return False
