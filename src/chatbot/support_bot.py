from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import logging
from settings import config
from dotenv import load_dotenv
from globals import vector_db
from src.utils.ContextAwareMemory import ContextAwareMemory

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupportBot:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-4o",
            openai_api_key=config.OPEN_API_KEY
        )
        self.memory = ContextAwareMemory()
        
        # Enhanced prompt template with vector DB context
        template = """You are a Remido support assistant (fintech/remittance).
        
        {history}
        
        Services: Int'l transfers, payments, fintech integration
        Features: Real-time tracking, multi-currency, secure API
        Users: Businesses, individuals, financial institutions
        
        Relevant Context:
        {context}
        
        Guidelines:
        - Be concise and professional
        - Focus on solutions
        - Use bullet points
        - Provide examples when needed
        
        Human: {input}
        Assistant:"""
        
        prompt = PromptTemplate(
            input_variables=["history", "input", "context"],
            template=template
        )
        
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )
    
    def _get_relevant_context(self, query: str) -> str:
        """Get relevant context from vector database."""
        try:
            results = vector_db.similarity_search(query, k=3)
            context = "\n".join([doc.page_content for doc in results])
            return context
        except Exception as e:
            logger.error(f"Error fetching context: {str(e)}")
            return ""
    
    def get_response(self, user_input: str) -> str:
        """Get a response from the bot while maintaining conversation history."""
        try:
            # Get relevant context from vector DB
            context = self._get_relevant_context(user_input)
            
            # Get response with context
            response = self.conversation.run(
                input=user_input,
                context=context
            )
            return response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.memory.clear() 