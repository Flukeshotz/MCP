import sys
import os
from mcp.server.fastmcp import FastMCP
from docs_tool import append_to_doc, find_or_create_doc, append_to_doc_blocks
from gmail_tool import create_email_draft

# Create the FastMCP instance
# allowed_hosts is required when deployed behind a reverse proxy (e.g. Railway)
# so that FastMCP's SSE handler accepts requests with the public domain as Host header.
mcp = FastMCP(
    "Google Docs & Gmail MCP Server",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    allowed_hosts=[
        "web-production-cdc1c.up.railway.app",
        "localhost",
        "127.0.0.1",
    ],
)

def prompt_approval(action_name: str, payload: dict) -> bool:
    """Prompts the user for approval in the terminal."""
    if os.environ.get("REQUIRE_APPROVAL", "true").lower() == "false":
        return True
        
    print(f"\n--- ACTION REQUIRED ---", file=sys.stderr)
    print(f"Action: {action_name}", file=sys.stderr)
    print(f"Payload: {payload}", file=sys.stderr)
    
    while True:
        try:
            choice = input("Approve? (y/n): ").strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Please enter 'y' or 'n'.", file=sys.stderr)
        except EOFError:
            return False

@mcp.tool()
def find_or_create_doc_tool(title: str) -> dict:
    """Finds or creates a Google Doc by title."""
    payload = {"title": title}
    if not prompt_approval("Find or Create Google Doc", payload):
        raise Exception("Action rejected by user")
        
    result = find_or_create_doc(title)
    if result.get("status") == "error":
        raise Exception(result.get("message"))
        
    return result

@mcp.tool()
def append_to_doc_blocks_tool(doc_id: str, blocks: list) -> dict:
    """Appends structured blocks to a Google Doc."""
    if not prompt_approval("Append Blocks to Google Doc", {"doc_id": doc_id, "blocks_count": len(blocks)}):
        raise Exception("Action rejected by user")
        
    result = append_to_doc_blocks(doc_id, blocks)
    if result.get("status") == "error":
        raise Exception(result.get("message"))
        
    return result

@mcp.tool()
def append_to_doc_tool(doc_id: str, content: str, bold: bool = False, italic: bool = False, underline: bool = False) -> dict:
    """Appends simple text to a Google Doc."""
    payload = {"doc_id": doc_id, "content": content, "bold": bold, "italic": italic, "underline": underline}
    if not prompt_approval("Append to Google Doc", payload):
        raise Exception("Action rejected by user")
        
    result = append_to_doc(doc_id, content, bold, italic, underline)
    if result.get("status") == "error":
        raise Exception(result.get("message"))
        
    return result

@mcp.tool()
def create_email_draft_tool(to: str, subject: str, body: str, is_html: bool = False) -> dict:
    """Creates a Gmail Draft."""
    payload = {"to": to, "subject": subject, "body": body, "is_html": is_html}
    if not prompt_approval("Create Gmail Draft", payload):
        raise Exception("Action rejected by user")
        
    result = create_email_draft(to, subject, body, is_html)
    if result.get("status") == "error":
        raise Exception(result.get("message"))
        
    return result

# Get the Starlette app for SSE
app = mcp.sse_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
