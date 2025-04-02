import re
from langchain_community.document_loaders import UnstructuredFileLoader, WebBaseLoader
import requests
import settings.config as config
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from src.data_preprocessors.preprocess_data import preprocess_data
from datetime import datetime, timedelta

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
            print(f"Warning: No content found in {link}")
    except Exception as e:
        print(f"Failed to fetch content from {link}: {e}")
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
                print(f"Warning: No content found in {file_url}")
        else:
            print(f"Failed to download file from Slack: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error processing document: {e}")
        return None
    
def fetch_slack_messages(channel_id, botToken):
    slack_client = WebClient(token=botToken)
    BOT_ID = slack_client.auth_test()["user_id"]
    
    url_pattern = r"https?://[^\s]+"  
    cursor = None
    messages = []
    seven_days_ago = int((datetime.utcnow() - timedelta(days=7)).timestamp())

    while True:
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
            if "files" in msg  and f"<@{BOT_ID}>" in msg["text"]:
                for file in msg["files"]:
                    if file["mimetype"].startswith("application"):  
                        file_content = fetch_content_from_document(file["url_private"], config.SLACK_BOT_TOKEN)
                        if file_content:
                            messages.append(file_content)

        cursor = response.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    return messages

