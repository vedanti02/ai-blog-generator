from src.data_loaders.slack_fetcher import fetch_slack_messages
from src.data_loaders.confluence_fetcher import fetch_confluence_data
from src.generators.summary_generator import generate_summary
from src.publishers.confluence_appender import append_to_confluence_page
from src.crud.store import store_data_vectordb
from src.event_listener.slack_listener import run_socket_mode
from src.data_preprocessors.preprocess_data import remove_bot_mentions, remove_duplicate_documents
from settings import config
import schedule, time
import threading
from globals import vector_db
import logging
from typing import List, Any
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApplicationError(Exception):
    """Custom exception for application-level errors."""
    pass

def run_summary_tasks(slack_docs_general: List[str], slack_docs_support: List[str], confluence_docs: List[Any]) -> None:
    """
    Run summary generation and posting tasks.
    
    Args:
        slack_docs_general: List of general Slack messages
        slack_docs_support: List of support Slack messages
        confluence_docs: List of Confluence documents
        
    Raises:
        ApplicationError: If summary generation or posting fails
    """
    try:
        # Generate initial summaries
        logger.info("Starting summary generation")
        slack_summary = generate_summary(slack_docs_general, "Slack")
        confluence_summary = generate_summary(
            [doc.page_content[:] for doc in confluence_docs], "Confluence"
        )
        logger.info("Successfully generated initial summaries")

        formatted_summary = f"""
            <h3>Slack Summary</h3>
            <p>{slack_summary}</p>
            <h3>Confluence Summary</h3>
            <p>{confluence_summary}</p>
            """

        # Support summary
        logger.info("Generating support summary")
        slack_support_summary = generate_summary(slack_docs_support, "Slack")
        formatted_support_summary = f"""
                <h3>Slack Summary</h3>
                <p>{slack_support_summary}</p>
            """
        logger.info("Successfully generated support summary")
        
        # Schedule the tasks
        def post_summary():
            try:
                logger.info("Posting general summary to Confluence")
                append_to_confluence_page(formatted_summary, "4423704")
                logger.info("Successfully posted general summary")
            except Exception as e:
                logger.error(f"Failed to post general summary: {e}")
                logger.error(traceback.format_exc())
        
        def post_support_summary():
            try:
                logger.info("Posting support summary to Confluence")
                append_to_confluence_page(formatted_support_summary, "5013506")
                logger.info("Successfully posted support summary")
            except Exception as e:
                logger.error(f"Failed to post support summary: {e}")
                logger.error(traceback.format_exc())

        schedule.every(60).seconds.do(post_summary)
        schedule.every(60).seconds.do(post_support_summary)
        logger.info("Scheduled summary posting tasks")

        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in schedule loop: {e}")
                logger.error(traceback.format_exc())
                time.sleep(5)  # Wait before retrying
                
    except Exception as e:
        logger.error(f"Error in summary tasks: {e}")
        logger.error(traceback.format_exc())
        raise ApplicationError(f"Failed to run summary tasks: {str(e)}")

def main():
    """
    Main application entry point.
    
    Raises:
        ApplicationError: If application initialization or execution fails
    """
    try:
        logger.info("Starting application initialization")
        
        # Fetch and process documents
        logger.info("Fetching Slack messages")
        slack_docs_general = fetch_slack_messages(config.SLACK_CHANNEL_ID, config.SLACK_BOT_TOKEN)
        slack_docs_support = fetch_slack_messages(config.SLACK_CHANNEL_ID, config.SLACK_BOT_TOKEN_SUPPORT)
        logger.info(f"Fetched {len(slack_docs_general)} general messages and {len(slack_docs_support)} support messages")

        logger.info("Fetching Confluence data")
        confluence_docs = fetch_confluence_data()
        logger.info(f"Fetched {len(confluence_docs)} Confluence documents")

        logger.info("Processing and combining documents")
        combined_docs = slack_docs_general + confluence_docs
        combined_docs_final = [remove_bot_mentions(doc) for doc in combined_docs]
        combined_docs_final = remove_duplicate_documents(combined_docs_final)
        logger.info(f"Processed {len(combined_docs_final)} combined documents")
        
        logger.info("Storing documents in vector database")
        store_data_vectordb(combined_docs_final, vector_db)
        logger.info("Successfully stored documents in vector database")
        
        logger.info("Starting summary thread")
        summary_thread = threading.Thread(
            target=run_summary_tasks,
            args=(slack_docs_general, slack_docs_support, confluence_docs)
        )
        summary_thread.daemon = True
        summary_thread.start()
        logger.info("Summary thread started successfully")
        
        # Run the socket mode handler as the main process
        logger.info("Starting Slack bot")
        run_socket_mode()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        logger.error(traceback.format_exc())
        raise ApplicationError(f"Application failed: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        logger.critical(traceback.format_exc())
        raise
