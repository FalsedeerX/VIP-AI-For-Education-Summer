from pydantic import BaseModel


class UserInfo(BaseModel):
    user_id: int


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str

class UserCourse(BaseModel):
    user_id: int
    course_code: str