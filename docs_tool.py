from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

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
