from pydantic import BaseModel


FolderContent = dict[str, str]


class NewFolder(BaseModel):
    folder_name: str
    course_id: int
    user_id: int


class FolderInfo(BaseModel):
    folder_id: int


class FolderOrganize(BaseModel):
    folder_id: int
    course_id: int
