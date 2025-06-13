from pydantic import BaseModel
from typing import List, Dict, Any

class NewChat(BaseModel):
    user_id: int  # 'user' or 'assistant'
    title: str

class ChatMessage(BaseModel):
    chat: List[Dict[str, Any]]

class NewChat(BaseModel):
    user_id: int  # ID of the user creating the chat
    message: str 
