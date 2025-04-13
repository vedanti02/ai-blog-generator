import settings.config as config
from atlassian import Confluence
from datetime import datetime
from requests.exceptions import RequestException
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def append_to_confluence_page(summary, pageId):
    try:
        confluence_url = config.CONFLUENCE_URL
        confluence_user = config.CONFLUENCE_USERNAME
        confluence_api_token = config.CONFLUENCE_API_KEY
        page_id = pageId

        confluence = Confluence(url=confluence_url, username=confluence_user, password=confluence_api_token)

        try:
            page = confluence.get_page_by_id(page_id, expand="body.storage,version")
            current_content = page["body"]["storage"]["value"]

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_summary = f"<h3>Summary - {timestamp}</h3><p>{summary}</p>"

            updated_content = new_summary + current_content

            # Update the page
            confluence.update_page(
                page_id=page_id,
                title=page["title"],
                body=updated_content,
                parent_id=None,
                type="page",
                representation="storage"
            )

            logger.info(f"Summary appended to Confluence at {timestamp}!")

        except RequestException as e:
            logger.error(f"Error communicating with Confluence: {str(e)}")
        except KeyError as e:
            logger.error(f"Error accessing page content: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while updating Confluence page: {str(e)}")

    except Exception as e:
        logger.error(f"Error initializing Confluence client: {str(e)}")