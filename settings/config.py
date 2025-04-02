import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Confluence
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_KEY = os.getenv("CONFLUENCE_API_KEY")
CONFLUENCE_SPACE = os.getenv("CONFLUENCE_SPACE")
CONFLUENCE_CREDENTIALS = os.getenv("CONFLUENCE_CREDENTIALS")

# Slack
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_BOT_TOKEN_SUPPORT = os.getenv("SLACK_BOT_TOKEN_SUPPORT")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_SIGNING_SECRET=os.getenv("SLACK_SIGNING_SECRET")

# ChromaDB
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")

#OpenAI
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
