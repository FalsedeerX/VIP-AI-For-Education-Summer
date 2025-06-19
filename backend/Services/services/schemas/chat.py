from pydantic import BaseModel
from typing import List, Dict, Any

class NewChat(BaseModel):
    user_id: int  
    title: str

ChatMessages = List[Dict[str, Any]]

class NewChatMessage(BaseModel):
    user_id: int  # ID of the user who sent the chat
    message: str 
