import settings.config as config
from atlassian import Confluence
from datetime import datetime

def append_to_confluence_page(summary, pageId):
    confluence_url = config.CONFLUENCE_URL
    confluence_user = config.CONFLUENCE_USERNAME
    confluence_api_token = config.CONFLUENCE_API_KEY
    page_id = pageId

    confluence = Confluence(url=confluence_url, username=confluence_user, password=confluence_api_token)

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

    print(f"Summary appended to Confluence at {timestamp}!")