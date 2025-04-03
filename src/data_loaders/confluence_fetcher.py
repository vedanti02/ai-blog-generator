import settings.config as config
from datetime import datetime, timedelta
from langchain_community.document_loaders import ConfluenceLoader
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

seven_days_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

CONFLUENCE_CREDENTIALS = {
    "url":config.CONFLUENCE_URL,
    "username":config.CONFLUENCE_USERNAME,
    "api_key":config.CONFLUENCE_API_KEY,
    "space_key":config.CONFLUENCE_SPACE,
    "limit":100,
    "include_attachments":True,
}

def fetch_confluence_data():
    try:
        confluence_loader = ConfluenceLoader(**CONFLUENCE_CREDENTIALS) 
        confluence_docs = confluence_loader.load()

        if not confluence_docs:
            logger.warning("No Confluence data found.")
            return []

        #fetch docs from last 7 days
        recent_docs = [
            doc for doc in confluence_docs 
            # if "lastModified" in doc.metadata and datetime.strptime(doc.metadata["lastModified"], "%Y-%m-%dT%H:%M:%S.%f%z") >= seven_days_ago
        ]
        return recent_docs

    except Exception as e:
        logger.error(f"Error fetching Confluence data: {str(e)}")
        return []