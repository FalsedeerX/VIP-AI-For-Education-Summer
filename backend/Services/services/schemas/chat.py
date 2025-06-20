from pydantic import BaseModel
from typing import List, Dict, Any


ChatMessages = List[Dict[str, Any]]


class NewChat(BaseModel):
    title: str


class NewChatMessage(BaseModel):
    message: str 
