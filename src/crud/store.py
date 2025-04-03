from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def store_data_vectordb(combined_docs, vector_db):
    try:
        combined_docs_final = [
            Document(page_content=doc) if isinstance(doc, str) else doc
            for doc in (combined_docs)
        ]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=70)
        split_docs = text_splitter.split_documents(combined_docs_final)
        
        # Store in ChromaDB
        total_docs = len(split_docs)
        for i in range(0, total_docs, 166):
            try:
                batch = split_docs[i:i + 166]
                # Store each batch in the vector database
                vector_db.add_documents(batch)
            except Exception as e:
                continue
                
    except Exception as e:
        logger.error(f"Error in store_data_vectordb: {str(e)}")
        raise