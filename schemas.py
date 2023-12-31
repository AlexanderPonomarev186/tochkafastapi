from pydantic import BaseModel, EmailStr, UUID4
from typing import Union

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    username: str
    password: str


class User(UserBase):
    id: UUID4
    is_active: bool

    class Config:
        orm_mode = True


class Login(BaseModel):
    login: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str


class Video(BaseModel):
    id: UUID4
    name: str
    video_path: str
    image_path:str
    user: str