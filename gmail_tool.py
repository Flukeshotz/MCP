import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

def create_email_draft(to: str, subject: str, body: str, is_html: bool = False) -> dict:
    """Creates an email draft in Gmail.
    
    Args:
        to: The recipient email address.
        subject: The email subject.
        body: The email body content.
        is_html: Whether the body is HTML formatted.
        
    Returns:
        dict: Response from the API containing draft ID.
    """
    creds = get_credentials()
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        message = EmailMessage()
        message['To'] = to
        message['From'] = 'me' # Gmail API infers the sender from 'me'
        message['Subject'] = subject

        if is_html:
            message.set_content(body, subtype='html')
        else:
            message.set_content(body)

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'message': {
                'raw': encoded_message
            }
        }
        
        draft = service.users().drafts().create(userId="me", body=create_message).execute()
        return {"status": "success", "draft_id": draft.get('id')}
        
    except HttpError as err:
        print(err)
        return {"status": "error", "message": str(err)}
