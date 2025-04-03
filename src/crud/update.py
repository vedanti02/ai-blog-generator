from langchain.schema import Document
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_data(from_text, to_text, vector_db, embeddings):
    try:
        results = vector_db.similarity_search(from_text, k=1)
        if results:
            updated_document = Document(
                id=results[0].id,
                metadata={"source":"updated"},
                page_content=to_text
            )

            vector_db.update_document(document_id=results[0].id, document=updated_document)
            logger.info(f"Successfully updated vector document with ID: {results[0].id}")
        else:
            logger.warning(f"No matching vector found for update with text: {from_text}")
    except Exception as e:
        logger.error(f"Error updating vector document: {str(e)}")
        raise