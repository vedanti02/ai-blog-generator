import re
from langchain_community.document_loaders import UnstructuredFileLoader, WebBaseLoader
import requests
import settings.config as config
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from src.data_preprocessors.preprocess_data import preprocess_data
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

slack_client = WebClient(token=config.SLACK_BOT_TOKEN)
socket_client = SocketModeClient(app_token=config.SLACK_APP_TOKEN)
BOT_ID = slack_client.auth_test()["user_id"]

def fetch_content_from_link(link):
    try:
        loader = WebBaseLoader(link)
        docs = loader.load()
        if docs:
            return preprocess_data(docs[0].page_content[:])
        else:
            logger.warning(f"No content found in {link}")
            return None
    except Exception as e:
        logger.error(f"Failed to fetch content from {link}: {str(e)}")
        return None

def fetch_content_from_document(file_url, header):
    headers = {"Authorization": f"Bearer {header}"}
    
    try:
        response = requests.get(file_url, headers=headers)
        if response.status_code == 200:
            temp_filename = "/tmp/slack_file"
            with open(temp_filename, "wb") as f:
                f.write(response.content)

            loader = UnstructuredFileLoader(temp_filename)
            docs = loader.load()
            if docs:
                return preprocess_data(docs[0].page_content[:])
            else:
                logger.warning(f"No content found in {file_url}")
                return None
        else:
            logger.error(f"Failed to download file from Slack: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return None
    
def fetch_slack_messages(channel_id, botToken):
    try:
        slack_client = WebClient(token=botToken)
        BOT_ID = slack_client.auth_test()["user_id"]
        
        url_pattern = r"https?://[^\s]+"  
        cursor = None
        messages = []
        seven_days_ago = int((datetime.utcnow() - timedelta(days=7)).timestamp())

        while True:
            try:
                response = slack_client.conversations_history(channel=channel_id, cursor=cursor, limit=200, oldest=seven_days_ago)

                for msg in response.get('messages', []):
                    if 'text' in msg and f"<@{BOT_ID}>" in msg['text']:  
                        message_text = msg['text']
                        found_links = re.findall(url_pattern, message_text)
                        messages.append(message_text)
                        
                        # Process links and store their content
                        for link in found_links:
                            link_content = fetch_content_from_link(link)
                            if link_content:
                                messages.append(link_content)
                    if "files" in msg and f"<@{BOT_ID}>" in msg["text"]:
                        for file in msg["files"]:
                            if file["mimetype"].startswith("application"):  
                                file_content = fetch_content_from_document(file["url_private"], config.SLACK_BOT_TOKEN)
                                if file_content:
                                    messages.append(file_content)

                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break

            except Exception as e:
                logger.error(f"Error processing Slack messages: {str(e)}")
                break

        return messages

    except Exception as e:
        logger.error(f"Error initializing Slack client: {str(e)}")
        return []

