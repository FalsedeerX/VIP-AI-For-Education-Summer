from pydantic import BaseModel
from uuid import UUID


FolderContent = dict[str, str]

class ChatOut(BaseModel):
    chat_id: UUID
    title: str

class NewFolder(BaseModel):
    folder_name: str
    course_id: int


class FolderInfo(BaseModel):
    folder_id: int


class FolderOrganize(BaseModel):
    folder_id: int
    course_id: int
