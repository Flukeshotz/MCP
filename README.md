# Google Docs & Gmail MCP Server

A FastAPI-based MCP-style server that provides tools to append content to Google Docs and create email drafts in Gmail.

## Project Structure
- `server.py`: FastAPI application with endpoints.
- `auth.py`: Handles Google OAuth 2.0 flow.
- `docs_tool.py`: Contains the logic to append text to Google Docs.
- `gmail_tool.py`: Contains the logic to create Gmail drafts.
- `requirements.txt`: Python dependencies.

## Setup Instructions

### 1. Google Cloud Console Setup
Before running the application, you need to configure an OAuth client in the Google Cloud Console.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services > Library** and enable the following APIs:
   - **Google Docs API**
   - **Gmail API**
4. Navigate to **APIs & Services > OAuth consent screen**:
   - Choose **External** (or Internal if you have a Google Workspace).
   - Fill in the required fields (App name, User support email, Developer contact information).
   - Under **Test users**, click **ADD USERS** and enter the email address you will use to test the application.
5. Navigate to **APIs & Services > Credentials**:
   - Click **CREATE CREDENTIALS > OAuth client ID**.
   - Select **Desktop app** as the Application type.
   - Name it (e.g., "MCP Server Local") and click **Create**.
   - Download the JSON file, rename it to `credentials.json`, and place it in the `google-mcp-server` directory.

### 2. Install Dependencies
Ensure you have Python 3.7+ installed. Run the following command in the `google-mcp-server` directory:

```bash
pip install -r requirements.txt
```

### 3. Initial Authentication
To generate the `token.json` file, run the `auth.py` script directly:

```bash
python auth.py
```

This will open a browser window for you to log in with your Google account (ensure you use the email added as a Test User in the consent screen). After granting permission, a `token.json` file will be created in your directory. You can close the browser window once authenticated.

### 4. Running the Server
Start the FastAPI server using `uvicorn`:

```bash
uvicorn server:app --reload
```
Alternatively, run `python server.py`.

The server will be running at `http://127.0.0.1:8000`. You can view the API documentation at `http://127.0.0.1:8000/docs`.

## Usage

When you make a request to the server, it will intercept the action and prompt you in the terminal for approval:

```text
--- ACTION REQUIRED ---
Action: Append to Google Doc
Payload: {'doc_id': '...', 'content': '...'}
Approve? (y/n):
```
You must type `y` in the terminal where the server is running to proceed.

### Example Request: Append to Doc
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/append_to_doc' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "doc_id": "YOUR_DOCUMENT_ID",
  "content": "\nThis is a new appended line!"
}'
```

### Example Request: Create Email Draft
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/create_email_draft' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "to": "example@example.com",
  "subject": "Test Draft",
  "body": "Hello, this is a draft from MCP Server!"
}'
```
