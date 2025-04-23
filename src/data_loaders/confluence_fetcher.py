from datetime import datetime, timedelta, timezone
from langchain_community.document_loaders import ConfluenceLoader
import settings.config as config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        recent_docs = []
        for doc in confluence_docs:
            modified = doc.metadata.get("when")
            if modified:
                try:
                    modified_date = datetime.strptime(modified, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                    if modified_date >= seven_days_ago:
                        recent_docs.append(doc)
                except ValueError as ve:
                    logger.warning(f"Failed to parse date: {modified} ({ve})")

        return recent_docs

    except Exception as e:
        logger.error(f"Error fetching Confluence data: {str(e)}")
        return []