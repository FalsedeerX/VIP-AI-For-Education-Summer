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