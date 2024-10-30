from pydantic import ConfigDict, EmailStr
from src.core.schemas import BaseModel


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    username: str
    password: str


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    username: str
    email: EmailStr
    hashed_password: str
    active: bool = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
