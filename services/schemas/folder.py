from pydantic import BaseModel

class FolderCreate(BaseModel):
    owner_id: int
    name: str

class FoldersWithChats(BaseModel):
    folders: dict[str, list[str]]

class FolderUpdate(BaseModel):
    chat_id: str
    folder_name: str 
