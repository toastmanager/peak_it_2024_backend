from typing import Annotated
from pydantic import StringConstraints
from pydantic_extra_types.phone_numbers import PhoneNumber
from src.core.schemas import BaseModel
from src.core.config import settings

auth_code_length = settings.auth.auth_code_length


class AuthCodeRequest(BaseModel):
    phone: Annotated[str, PhoneNumber]


class AuthCodeVerify(AuthCodeRequest):
    code: Annotated[
        str,
        StringConstraints(
            max_length=auth_code_length,
            min_length=auth_code_length,
        ),
    ]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
