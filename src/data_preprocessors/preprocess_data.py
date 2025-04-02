import re
from bs4 import BeautifulSoup

def remove_bot_mentions(text):
    """Remove bot mentions while preserving the original document format."""
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Remove bot mentions (e.g., <@BOT_ID>)
    text = re.sub(r'<@[^>]+>', '', text)
    
    return text

def preprocess_data(text):
    if not text:
        return ""
    
    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # Remove multiple spaces, tabs, and newlines
    text = re.sub(r'\s+', ' ', text)

    # Remove leading and trailing spaces
    text = text.strip()

    return text

def remove_duplicate_documents(documents):
    """Remove duplicate documents based on their content."""
    if not documents:
        return []
    
    # Convert all documents to strings if they aren't already
    doc_strings = [str(doc) if not isinstance(doc, str) else doc for doc in documents]
    
    # Use a set to track unique documents
    unique_docs = []
    seen = set()
    
    for doc in doc_strings:
        # Normalize the document content by removing extra whitespace
        normalized_doc = ' '.join(doc.split())
        if normalized_doc not in seen:
            seen.add(normalized_doc)
            unique_docs.append(doc)
    
    return unique_docs
