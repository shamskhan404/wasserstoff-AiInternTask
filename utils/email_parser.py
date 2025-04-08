from gmail.gmail_auth import get_gmail_service
from database.db_handler import store_email
import base64

def fetch_and_store_emails():
    service = get_gmail_service()
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
        messages = results.get('messages', [])

        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            payload = msg_detail.get('payload', {})
            headers = payload.get('headers', [])
            parts = payload.get('parts', [])

            email_data = {
                'id': msg['id'],
                'snippet': msg_detail.get('snippet', ''),
                'body': get_body_from_payload(payload),
                'subject': get_header(headers, 'Subject'),
                'sender': get_header(headers, 'From'),
                'recipient': get_header(headers, 'To'),
                'timestamp': get_header(headers, 'Date'),
                'in_reply_to': get_in_reply_to(headers),
                'thread_id': msg_detail.get('threadId'),
                'has_attachment': has_attachments(parts)
            }
            store_email(email_data)
    except Exception as e:
        print(f"[ERROR] Error fetching and storing emails: {e}")

def get_body_from_payload(payload):
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body += part['body'].get('data', '')
            elif part['mimeType'] == 'text/html':
                pass
            elif part['mimeType'] == 'multipart/alternative':
                for sub_part in part['parts']:
                    if sub_part['mimeType'] == 'text/plain':
                        body += sub_part['body'].get('data', '')
    elif payload.get('mimeType') == 'text/plain':
        body = payload['body'].get('data', '')
    return base64_decode(body)

def get_header(headers, name):
    for header in headers:
        if header['name'] == name:
            return header['value']
    return ''

def get_in_reply_to(headers):
    return get_header(headers, 'In-Reply-To')

def has_attachments(parts):
    if parts:
        for part in parts:
            if part.get('filename'):
                return True
            if part.get('parts'):
                if has_attachments(part['parts']):
                    return True
    return False

def base64_decode(data):
    if data:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return ''