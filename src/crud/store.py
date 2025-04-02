from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def store_data_vectordb(combined_docs, vector_db):
    combined_docs_final = [
        Document(page_content=doc) if isinstance(doc, str) else doc
        for doc in (combined_docs)
    ]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=70)
    split_docs = text_splitter.split_documents(combined_docs_final)
    # Store in ChromaDB
    for i in range(0, len(split_docs), 166):
        batch = split_docs[i:i + 166]
        # Store each batch in the vector database
        vector_db.add_documents(batch)