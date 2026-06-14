from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
from docs_tool import append_to_doc, find_or_create_doc, append_to_doc_blocks
from gmail_tool import create_email_draft

app = FastAPI(title="Google Docs & Gmail MCP Server")

class DocAppendRequest(BaseModel):
    doc_id: str
    content: str
    bold: bool = False
    italic: bool = False
    underline: bool = False

class DocFindOrCreateRequest(BaseModel):
    title: str

class DocAppendBlocksRequest(BaseModel):
    doc_id: str
    blocks: list

class EmailDraftRequest(BaseModel):
    to: str
    subject: str
    body: str
    is_html: bool = False

def prompt_approval(action_name: str, payload: dict) -> bool:
    """Prompts the user for approval in the terminal."""
    if os.environ.get("REQUIRE_APPROVAL", "true").lower() == "false":
        return True
        
    print(f"\n--- ACTION REQUIRED ---", file=sys.stderr)
    print(f"Action: {action_name}", file=sys.stderr)
    print(f"Payload: {payload}", file=sys.stderr)
    
    # We read from sys.stdin to avoid issues if input() gets confused by Uvicorn's loops
    # Or simply use input() which normally reads from stdin
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

@app.post("/find_or_create_doc")
def api_find_or_create_doc(request: DocFindOrCreateRequest):
    payload = request.model_dump()
    if not prompt_approval("Find or Create Google Doc", payload):
        raise HTTPException(status_code=403, detail="Action rejected by user")
        
    result = find_or_create_doc(request.title)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result

@app.post("/append_to_doc_blocks")
def api_append_to_doc_blocks(request: DocAppendBlocksRequest):
    payload = request.model_dump()
    if not prompt_approval("Append Blocks to Google Doc", {"doc_id": request.doc_id, "blocks_count": len(request.blocks)}):
        raise HTTPException(status_code=403, detail="Action rejected by user")
        
    result = append_to_doc_blocks(request.doc_id, request.blocks)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result

@app.post("/append_to_doc")
def api_append_to_doc(request: DocAppendRequest):
    payload = request.model_dump()
    if not prompt_approval("Append to Google Doc", payload):
        raise HTTPException(status_code=403, detail="Action rejected by user")
        
    result = append_to_doc(request.doc_id, request.content, request.bold, request.italic, request.underline)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result

@app.post("/create_email_draft")
def api_create_email_draft(request: EmailDraftRequest):
    payload = request.model_dump()
    if not prompt_approval("Create Gmail Draft", payload):
        raise HTTPException(status_code=403, detail="Action rejected by user")
        
    result = create_email_draft(request.to, request.subject, request.body, request.is_html)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
