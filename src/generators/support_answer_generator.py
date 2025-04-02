from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from settings import config


def support_answer_generator(question, vector_db):
    """Generates an answer based on retrieved documents from the vector database."""
    
    chat_model = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=config.OPEN_API_KEY)
    
    docs = vector_db.as_retriever(k=4).invoke(question)

    system_prompt = """
    Answer the user's question based on the provided context.
    If the context does not contain relevant information, reply with: "I don't know."

    <context>
    {context}
    </context>
    """

    # Create chat prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    document_chain = create_stuff_documents_chain(chat_model, prompt_template)

    return document_chain.invoke({
        "context": docs,
        "messages": [HumanMessage(content=question)],
    })
