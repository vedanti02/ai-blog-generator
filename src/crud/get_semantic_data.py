from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the model with error handling
try:
    # Use a smaller model if memory is an issue
    model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    logger.info("Successfully loaded sentence transformer model")
except Exception as e:
    logger.error(f"Failed to load sentence transformer model: {e}")
    raise

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using sentence-transformers with error handling."""
    try:
        if not texts:
            logger.warning("No texts provided for embedding")
            return []
        
        # Ensure texts are strings
        texts = [str(text) for text in texts]
        
        # Generate embeddings
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return []

def get_relevant_docs(examples: List[Dict[str, Any]], keyword: str, top_k: int = 3) -> List[str]:
    """
    Get relevant documents based on semantic similarity to the keyword.
    
    Args:
        examples: List of documents to search through
        keyword: The keyword to find relevant documents for
        top_k: Number of most relevant documents to return
        
    Returns:
        List of relevant document contents
    """
    try:
        if not examples:
            logger.warning("No examples provided")
            return []
            
        if not keyword:
            logger.warning("No keyword provided")
            return []
            
        # Get embeddings for all documents
        doc_texts = [example["content"] for example in examples]
        doc_embeddings = get_embeddings(doc_texts)
        
        if not doc_embeddings:
            logger.warning("No document embeddings generated")
            return []
            
        # Get embedding for the keyword
        keyword_embedding = get_embeddings([keyword])
        if not keyword_embedding:
            logger.warning("No keyword embedding generated")
            return []
        keyword_embedding = keyword_embedding[0]
        
        # Calculate similarities
        similarities = []
        for doc_embedding in doc_embeddings:
            try:
                similarity = np.dot(keyword_embedding, doc_embedding) / (
                    np.linalg.norm(keyword_embedding) * np.linalg.norm(doc_embedding)
                )
                similarities.append(similarity)
            except Exception as e:
                logger.error(f"Error calculating similarity: {e}")
                similarities.append(0)  # Default to 0 similarity if calculation fails
        
        # Get top k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        relevant_docs = [doc_texts[i] for i in top_indices]
        
        logger.info(f"Successfully retrieved {len(relevant_docs)} relevant documents for keyword: {keyword}")
        return relevant_docs
        
    except Exception as e:
        logger.error(f"Error in get_relevant_docs: {e}")
        return []