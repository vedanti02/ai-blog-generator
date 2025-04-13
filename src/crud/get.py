import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_data(word: str, vector_db) -> List[str]:
    """
    Get similar documents using vector store's similarity search.
    
    Args:
        word: The query word to search for
        vector_db: The vector store instance
        
    Returns:
        List of similar document contents (limited to 3 documents)
    """
    try:
        # Use similarity_search to find relevant documents, limit to 3
        results = vector_db.similarity_search(word, k=3)
        content_list = [result.page_content for result in results]
        logger.info(f"Successfully retrieved {len(content_list)} results for word: {word}")
        return content_list
    except Exception as e:
        logger.error(f"Error retrieving data for word '{word}': {str(e)}")
        return []