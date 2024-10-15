import uuid

from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from src.auth.schemas import UserCreate, UserRead
from src.auth.dependencies import get_user_manager
from src.auth.models import User
from src.auth.auth import auth_backend

router = APIRouter(
    tags=["auth"]
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)