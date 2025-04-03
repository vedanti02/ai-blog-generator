from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

GOOGLE_DOCS_SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.file"]
SERVICE_ACCOUNT_FILE = "key.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def upload_to_google_docs(title, content):
    """Uploads blog content to Google Docs and returns a shareable link."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=GOOGLE_DOCS_SCOPES
        )

        docs_service = build("docs", "v1", credentials=credentials)
        drive_service = build("drive", "v3", credentials=credentials)

        try:
            # Create the document
            document = docs_service.documents().create(body={"title": title}).execute()
            doc_id = document["documentId"]

            # Update the document content
            requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
            docs_service.documents().batchUpdate(
                documentId=doc_id, 
                body={"requests": requests}
            ).execute()

            # Set sharing permissions
            permission = {"type": "anyone", "role": "writer"}
            drive_service.permissions().create(
                fileId=doc_id, 
                body=permission
            ).execute()

            # Generate Document Link
            doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
            logger.info(f"Google Doc created successfully: {doc_link}")
            return doc_link

        except HttpError as e:
            logger.error(f"Google API error occurred: {str(e)}")
            raise
        except KeyError as e:
            logger.error(f"Error accessing document properties: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating Google Doc: {str(e)}")
            raise

    except FileNotFoundError:
        logger.error(f"Service account key file not found: {SERVICE_ACCOUNT_FILE}")
        raise
    except Exception as e:
        logger.error(f"Error initializing Google services: {str(e)}")
        raise
