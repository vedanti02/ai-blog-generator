from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.chatbot.support_bot import SupportBot
from typing import Dict

router = APIRouter()
support_bot = SupportBot()

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/support/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = support_bot.get_response(request.message)
        return ChatResponse(
            response=response,
            session_id=request.session_id or "default"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/support/clear")
async def clear_history():
    try:
        support_bot.clear_history()
        return {"message": "Conversation history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 