
def get_data(word, vector_db):
    results = vector_db.similarity_search(word, k=3)
    return [result.page_content for result in results]