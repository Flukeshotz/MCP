from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials
from typing import List, Dict, Any

def find_or_create_doc(title: str) -> dict:
    """Finds a Google Doc by title, or creates it if it doesn't exist.
    
    Args:
        title: The title of the document.
        
    Returns:
        dict: containing 'document_id'
    """
    creds = get_credentials()
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        # Search for existing file
        query = f"name='{title}' and mimeType='application/vnd.google-apps.document' and trashed=false"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if items:
            return {"status": "success", "document_id": items[0]['id']}
            
        # If not found, create via Docs API
        docs_service = build('docs', 'v1', credentials=creds)
        body = {'title': title}
        doc = docs_service.documents().create(body=body).execute()
        return {"status": "success", "document_id": doc.get('documentId')}
        
    except HttpError as err:
        print(err)
        return {"status": "error", "message": str(err)}

def append_to_doc_blocks(doc_id: str, blocks: List[Dict[str, Any]]) -> dict:
    """Appends structured blocks (headings, paragraphs, bullets) to a Google Doc.
    
    Args:
        doc_id: The ID of the document.
        blocks: A list of dicts with 'type' and 'text'.
    """
    creds = get_credentials()
    try:
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=doc_id).execute()
        body_content = document.get('body').get('content')
        end_index = body_content[-1].get('endIndex') - 1
        
        requests = []
        
        # Build text string backwards to maintain stable indices, or just build one giant string
        # Actually, the easiest way is to insert all text at once, then format the ranges.
        # But wait, Docs API insertText inserts at a specific index. If we do it in one batch,
        # we can insert all text, then apply styles.
        
        full_text = "\n"
        style_ranges = []
        current_idx = end_index + 1 # +1 because of the initial \n
        
        for block in blocks:
            b_type = block.get("type", "paragraph")
            text = block.get("text", "")
            
            if b_type == "heading_1":
                prefix = ""
                suffix = "\n\n"
                style = "HEADING_1"
            elif b_type == "heading_2":
                prefix = ""
                suffix = "\n"
                style = "HEADING_2"
            elif b_type == "bullet":
                # Google docs has native bullets but it's complex via API.
                # A simple bullet character works beautifully.
                prefix = "• "
                suffix = "\n"
                style = "NORMAL_TEXT"
            else:
                prefix = ""
                suffix = "\n\n"
                style = "NORMAL_TEXT"
                
            block_text = prefix + text + suffix
            start = current_idx
            end = current_idx + len(block_text)
            
            full_text += block_text
            style_ranges.append({
                "style": style,
                "start": start,
                "end": end
            })
            current_idx = end
            
        full_text += "\n---\n"
        
        # 1. Insert the text
        requests.append({
            'insertText': {
                'location': {'index': end_index},
                'text': full_text
            }
        })
        
        # 2. Apply paragraph styles
        for sr in style_ranges:
            if sr["style"] in ("HEADING_1", "HEADING_2"):
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': sr["start"],
                            'endIndex': sr["end"]
                        },
                        'paragraphStyle': {
                            'namedStyleType': sr["style"]
                        },
                        'fields': 'namedStyleType'
                    }
                })
                
        result = service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        return {"status": "success", "result": result}
        
    except HttpError as err:
        print(err)
        return {"status": "error", "message": str(err)}


def append_to_doc(doc_id: str, content: str, bold: bool = False, italic: bool = False, underline: bool = False) -> dict:
    """Appends content to the end of a Google Doc.
    
    Args:
        doc_id: The ID of the document to modify.
        content: The text to append.
        bold: Whether to apply bold formatting.
        italic: Whether to apply italic formatting.
        underline: Whether to apply underline formatting.
        
    Returns:
        dict: Response from the API.
    """
    creds = get_credentials()
    try:
        service = build('docs', 'v1', credentials=creds)
        
        # We need to get the document to find its end index
        document = service.documents().get(documentId=doc_id).execute()
        
        # The content of the document is a list of StructuralElements.
        # We find the end index of the body.
        body_content = document.get('body').get('content')
        end_index = body_content[-1].get('endIndex') - 1
        
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': end_index,
                    },
                    'text': content
                }
            }
        ]
        
        if bold or italic or underline:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': end_index,
                        'endIndex': end_index + len(content)
                    },
                    'textStyle': {
                        'bold': bold,
                        'italic': italic,
                        'underline': underline
                    },
                    'fields': 'bold,italic,underline'
                }
            })
        
        result = service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
            
        return {"status": "success", "result": result}
        
    except HttpError as err:
        print(err)
        return {"status": "error", "message": str(err)}
