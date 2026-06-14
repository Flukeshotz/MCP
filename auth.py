import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/gmail.compose'
]

def get_credentials():
    """Gets valid user credentials from storage.
    
    If nothing is found, it will start the OAuth flow.
    """
    creds = None
    
    # Check environment variable first, then fallback to file
    token_json_str = os.environ.get('GOOGLE_TOKEN_JSON')
    if token_json_str:
        token_data = json.loads(token_json_str)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    elif os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            if creds_json_str:
                creds_data = json.loads(creds_json_str)
                flow = InstalledAppFlow.from_client_config(creds_data, SCOPES)
            elif os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            else:
                raise FileNotFoundError("credentials.json not found locally and GOOGLE_CREDENTIALS_JSON environment variable not set.")
            
            # If deployed in cloud (e.g. Railway), we cannot launch a browser
            if os.environ.get("REQUIRE_APPROVAL", "true").lower() == "false":
                raise RuntimeError("Authentication failed in cloud environment. Please ensure GOOGLE_TOKEN_JSON is set correctly in Railway variables.")
                
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run (only if not in cloud)
        if os.environ.get("REQUIRE_APPROVAL", "true").lower() != "false":
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            
    return creds

if __name__ == '__main__':
    # When run directly, this will trigger the OAuth flow and generate token.json
    print("Initiating authentication flow...")
    get_credentials()
    print("Authentication successful! token.json has been generated.")
