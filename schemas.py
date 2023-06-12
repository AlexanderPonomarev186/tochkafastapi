from pydantic import BaseModel, EmailStr, UUID4
from typing import Union

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
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
    video_path: str