from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from settings import config
from src.crud.get import get_data
from src.crud.update import update_data
from globals import vector_db, embeddings, keyword_storage
from src.generators.blog_generator import BlogGenerationError, BlogGenerator
from src.chatbot.support_bot import SupportBot
import logging
from typing import Optional, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

blog_generator = BlogGenerator()

class SlackListenerError(Exception):
    """Custom exception for Slack listener errors."""
    pass

# Initialize Slack app
try:
    app = App(
        token=config.SLACK_BOT_TOKEN,
        signing_secret=config.SLACK_SIGNING_SECRET
    )
    bot_info = app.client.auth_test()
    BOT_USER_ID = bot_info["user_id"]
except Exception as e:
    logger.error(f"Failed to initialize Slack app: {e}")
    raise SlackListenerError("Failed to initialize Slack application")

# Initialize support bot
try:
    support_bot = SupportBot()
except Exception as e:
    logger.error(f"Failed to initialize support bot: {e}")
    raise SlackListenerError("Failed to initialize support bot")

def handle_error(error: Exception, respond: Optional[callable] = None) -> None:
    """
    Handle errors in a consistent way across the application.
    
    Args:
        error: The exception that occurred
        respond: Optional Slack respond function to send error message
    """
    error_message = f"An error occurred: {str(error)}"
    logger.error(error_message)
    
    if respond:
        try:
            respond(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message to Slack: {e}")

@app.command("/blog")
def handle_blog_command(ack, respond, command):
    """Handle /blog command with error handling."""
    try:
        ack()
        keyword = command["text"].strip()
        
        if not keyword:
            respond("Please provide a keyword. Example: `/blog remittance`")
            return
        
        respond(f"Generating blog for keyword: *{keyword}*")
        keyword_storage["keyword"] = keyword  
        logger.info(f"Blog generation started for {keyword}")
        
        try:
            blog_generator.generate_blogs(vector_db, embeddings, keyword=keyword)
        except BlogGenerationError as e:
            handle_error(e, respond)
        except Exception as e:
            handle_error(e, respond)
            
    except Exception as e:
        handle_error(e, respond)

@app.command("/get")
def handle_get_command(ack, respond, command):
    """Handle /get command with error handling."""
    try:
        ack()
        sentence = command["text"].strip()
        
        if not sentence:
            respond("Please provide input. Example: `/get Remido`")
            return
        
        respond(f"Getting information for: *{sentence}*")
        try:
            results = get_data(sentence, vector_db)
            respond(f"Results for *{sentence}: *{results}")
        except Exception as e:
            handle_error(e, respond)
            
    except Exception as e:
        handle_error(e, respond)

@app.command("/update")
def open_modal(ack, command, client):
    """Handle /update command with error handling."""
    try:
        ack()
        client.views_open(
            trigger_id=command["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "update_text",
                "title": {"type": "plain_text", "text": "Update Text"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "from_text",
                        "element": {"type": "plain_text_input", "action_id": "from"},
                        "label": {"type": "plain_text", "text": "From"},
                    },
                    {
                        "type": "input",
                        "block_id": "to_text",
                        "element": {"type": "plain_text_input", "action_id": "to"},
                        "label": {"type": "plain_text", "text": "To"},
                    },
                ],
                "submit": {"type": "plain_text", "text": "Update"},
                "close": {"type": "plain_text", "text": "Cancel"},
            },
        )
    except Exception as e:
        handle_error(e)
        logger.error(f"Error opening modal: {e}")

@app.view("update_text")
def handle_submission(ack, body, client):
    """Handle modal submission with error handling."""
    try:
        ack()
        from_text = body["view"]["state"]["values"].get("from_text", {}).get("from", {}).get("value", "")
        to_text = body["view"]["state"]["values"].get("to_text", {}).get("to", {}).get("value", "")

        if not from_text or not to_text:
            raise ValueError("Both 'From' and 'To' fields are required")

        try:
            update_data(from_text, to_text, vector_db, embeddings)
            updated_text = f"Replaced *{from_text}* with *{to_text}*"
            client.chat_postMessage(channel=config.SLACK_CHANNEL_ID, text=updated_text)
        except Exception as e:
            handle_error(e)
            client.chat_postMessage(
                channel=config.SLACK_CHANNEL_ID,
                text=f"Failed to update text: {str(e)}"
            )
    except Exception as e:
        handle_error(e)
        ack({"response_action": "errors", "errors": {"from_text": str(e)}})

@app.command("/support")
def handle_support_command(ack, respond, command):
    """Handle /support command with error handling."""
    try:
        ack()
        sentence = command["text"].strip()
        
        if not sentence:
            respond("Please provide your question. Example: `/support what is remido?`")
            return

        user_id = command["user_id"]
        logger.info(f"Support request from user {user_id}: {sentence}")

        try:
            response = support_bot.get_response(sentence)
            app.client.chat_postMessage(
                channel=config.SLACK_CHANNEL_ID,
                text=f"User {user_id} asked: {sentence}\nResponse: {response}"
            )
        except Exception as e:
            handle_error(e, respond)
            
    except Exception as e:
        handle_error(e, respond)

def run_socket_mode():
    """Run the Slack socket mode handler with error handling."""
    try:
        handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)
        handler.start()
    except Exception as e:
        logger.error(f"Failed to start Slack socket mode: {e}")
        raise SlackListenerError(f"Failed to start Slack socket mode: {str(e)}")

if __name__ == "__main__":
    try:
        logger.info("Starting Slack bot...")
        run_socket_mode()
    except Exception as e:
        logger.error(f"Fatal error in Slack bot: {e}")
        raise 
