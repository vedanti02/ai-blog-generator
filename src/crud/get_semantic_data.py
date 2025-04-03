from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_chroma import Chroma
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_relevant_docs(examples, embeddings, keyword):
    try:
        example_selector = SemanticSimilarityExampleSelector.from_examples(
            examples=examples, 
            embeddings=embeddings,
            vectorstore_cls=Chroma,
            k=5 
        )
        selected_examples = example_selector.select_examples({"query": keyword})
        relevant_docs = [example["content"] for example in selected_examples]
        logger.info(f"Successfully retrieved {len(relevant_docs)} relevant documents for keyword: {keyword}")
        return relevant_docs
    except Exception as e:
        logger.error(f"Error retrieving relevant documents: {str(e)}")
        return []