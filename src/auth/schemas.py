import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    email: str | None


class UserCreate(schemas.BaseUserCreate):
    phone: str
    email: str | str


class UserUpdate(schemas.BaseUserUpdate):
    pass
