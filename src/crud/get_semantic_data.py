from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_chroma import Chroma


def get_relevant_docs(examples, embeddings, keyword):
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples=examples, 
        embeddings=embeddings,
        vectorstore_cls=Chroma,
        k=5 
    )
    return [example["content"] for example in example_selector.select_examples({"query": keyword})]