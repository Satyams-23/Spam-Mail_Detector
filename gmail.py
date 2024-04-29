# gmail.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import base64

# Define the scopes for accessing Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Authenticate with Gmail API
def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8000)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

# Fetch emails
def fetch_emails():
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])
    
    emails = []
    if messages:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg['payload']
            headers = payload['headers']
            email_info = {}
            for header in headers:
                if header['name'] == 'From':
                    email_info['from'] = header['value']
                elif header['name'] == 'Subject':
                    email_info['subject'] = header['value']
                elif header['name'] == 'Date':
                    email_info['date'] = header['value']
            emails.append((message['id'], email_info))  # Store message ID along with email info
    return emails

# Fetch email message content by message ID
def fetch_email_content(message_id):
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    payload = message.get('payload', {})
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType', '') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                    return decoded_data
    return "No content available for this message"
