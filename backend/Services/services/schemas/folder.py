from pydantic import BaseModel


FoldersWithChats = dict[str, list[str]]


class FolderCreate(BaseModel):
    folder_name: str


class FolderUpdate(BaseModel):
    folder_name: str 
    chat_id: str
