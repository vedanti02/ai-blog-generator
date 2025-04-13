from langchain_chroma import Chroma
from settings import config
from slack_bolt import App
import chromadb
from src.utils.embeddings import EmbeddingFunction

persistent_client = chromadb.PersistentClient()
collection = persistent_client.get_or_create_collection("collection_name")

# Create embedding function instance
embedding_function = EmbeddingFunction()

# Create and store global instances here
vector_db = Chroma(
    collection_name="blog_data",
    embedding_function=embedding_function,
    client=persistent_client,
    persist_directory=config.CHROMA_DB_PATH
)
keyword_storage = {"keyword": None}