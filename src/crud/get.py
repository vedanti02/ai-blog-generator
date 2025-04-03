import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_data(word, vector_db):
    try:
        results = vector_db.similarity_search(word, k=3)
        content_list = [result.page_content for result in results]
        logger.info(f"Successfully retrieved {len(content_list)} results for word: {word}")
        return content_list
    except Exception as e:
        logger.error(f"Error retrieving data for word '{word}': {str(e)}")
        return []