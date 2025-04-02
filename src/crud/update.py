from langchain.schema import Document

def update_data(from_text,to_text, vector_db, embeddings):
    
    results = vector_db.similarity_search(from_text, k=1)
    if results:
        updated_document = Document(
            id=results[0].id,
            metadata={"source":"updated"},
            page_content=to_text
        )

        vector_db.update_document(document_id = results[0].id, document = updated_document)

        print("Vector updated successfully.")
    else:
        print("No matching vector found for update.")