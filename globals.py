from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from settings import config
from slack_bolt import App
import chromadb

persistent_client = chromadb.PersistentClient()
collection = persistent_client.get_or_create_collection("collection_name")

# Create and store global instances here
embeddings = OpenAIEmbeddings(api_key=config.OPEN_API_KEY)
vector_db = Chroma(collection_name="blog_data", embedding_function=embeddings, client=persistent_client, persist_directory=config.CHROMA_DB_PATH)
keyword_storage = {"keyword": None}