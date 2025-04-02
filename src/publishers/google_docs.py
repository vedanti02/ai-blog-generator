from google.oauth2 import service_account
from googleapiclient.discovery import build

GOOGLE_DOCS_SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.file"]
SERVICE_ACCOUNT_FILE = "key.json"

def upload_to_google_docs(title, content):
    """Uploads blog content to Google Docs and returns a shareable link."""

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=GOOGLE_DOCS_SCOPES
    )

    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    document = docs_service.documents().create(body={"title": title}).execute()
    doc_id = document["documentId"]

    requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

    permission = {"type": "anyone", "role": "writer"}
    drive_service.permissions().create(fileId=doc_id, body=permission).execute()

    # Generate Document Link
    doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"

    print(f"Google Doc created: {doc_link}")
    return doc_link
