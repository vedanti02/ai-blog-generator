from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import os
from settings import config
from dotenv import load_dotenv

load_dotenv()

class SupportBot:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-4-turbo-preview",
            openai_api_key=config.OPEN_API_KEY
        )
        self.memory = ConversationBufferMemory()
        
        # Enhanced prompt template with more context about Remido
        template = """You are a knowledgeable support assistant for Remido, a financial technology company specializing in remittance and payment solutions. 
        You have access to the following conversation history:
        
        {history}
        
        Important Context about Remido:
        1. Core Services:
           - Remittance services for international money transfers
           - Payment processing solutions
           - Financial technology integration
           - Cross-border payment capabilities
        
        2. Key Features:
           - Real-time transaction tracking
           - Multi-currency support
           - Secure payment processing
           - API integration capabilities
           - Compliance with international financial regulations
        
        3. Target Users:
           - Businesses requiring international payment solutions
           - Individuals sending money abroad
           - Financial institutions
           - E-commerce platforms
        
        4. Technical Capabilities:
           - RESTful API integration
           - Webhook support
           - Multi-language support
           - 24/7 transaction monitoring
        
        Guidelines for Responses:
        1. Be professional and friendly
        2. Provide specific, actionable information
        3. Include relevant technical details when appropriate
        4. Maintain context from previous questions
        5. If unsure about specific details, acknowledge limitations
        6. Use bullet points for multiple features or steps
        7. Include examples when relevant
        
        Human: {input}
        Assistant:"""
        
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template
        )
        
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )
    
    def get_response(self, user_input: str) -> str:
        """Get a response from the bot while maintaining conversation history."""
        try:
            response = self.conversation.predict(input=user_input)
            return response
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.memory.clear() 