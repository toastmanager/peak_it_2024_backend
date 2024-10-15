import uuid

from fastapi_users import schemas
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserRead(schemas.BaseUser[uuid.UUID]):
    phone: PhoneNumber
    email: EmailStr | None


class UserCreate(schemas.BaseUserCreate):
    phone: PhoneNumber
    email: EmailStr | None


class UserUpdate(schemas.BaseUserUpdate):
    pass
