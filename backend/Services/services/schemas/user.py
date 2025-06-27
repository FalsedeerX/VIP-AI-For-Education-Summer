from typing import Any, Dict, List
from pydantic import BaseModel


class UserInfo(BaseModel):
    user_id: int


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool


class UserLogin(BaseModel):
    username: str
    password: str

class UserCourse(BaseModel):
    course_code: str

UserCourseList = List[Dict[str, Any]]