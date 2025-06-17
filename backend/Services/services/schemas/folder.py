from pydantic import BaseModel

class FolderCreate(BaseModel):
    owner_id: int
    name: str

FoldersWithChats = dict[str, list[str]]

class FolderUpdate(BaseModel):
    chat_id: str
    folder_name: str 
