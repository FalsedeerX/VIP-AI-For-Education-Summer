from pydantic import BaseModel
from typing import List, Dict, Any


ChatMessages = List[Dict[str, Any]]

#class ChatMessages(BaseModel):
#    messages: List[Dict[str, Any]]
#    owner_id: str

class ChatOwner(BaseModel):
    owner_id: int


class NewChat(BaseModel):
    title: str


class ChatOrganize(BaseModel):
    folder_id: int
    chat_id: str


class NewChatMessage(BaseModel):
    message: str 
