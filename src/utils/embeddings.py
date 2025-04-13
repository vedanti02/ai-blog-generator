from sentence_transformers import SentenceTransformer
import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingFunction:
    def __init__(self):
        try:
            self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
            logger.info("Successfully loaded sentence transformer model")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer model: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        try:
            if not text:
                logger.warning("No text provided for embedding")
                return []
            return self.model.encode([text])[0].tolist()
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
        try:
            if not texts:
                logger.warning("No texts provided for embedding")
                return []
            
            # Ensure texts are strings
            texts = [str(text) for text in texts]
            
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            return [] 