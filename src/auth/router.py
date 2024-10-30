from fastapi import APIRouter, Depends, Form

from src.auth.dependencies import get_auth_service, get_current_active_auth_user
from src.auth.schemas import CreateUser, Token, UserSchema
from src.auth.service import AuthService

auth_router = APIRouter(prefix="/jwt", tags=["JWT"])


@auth_router.post("/login", response_model=Token)
async def auth_user_issue_jwt(
    username: str = Form(),
    password: str = Form(),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(username=username, password=password)


@auth_router.post("/register", response_model=Token)
async def create_new_user(
    create_user_schema: CreateUser,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.create_user(create_user_schema=create_user_schema)


@auth_router.post("/refresh", response_model=Token)
async def refresh_jwt(
    refresh_token: str = Form(), auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    payload = auth_service.get_current_token_payload(refresh_token)
    token: Token = await auth_service.refresh_token(payload)
    return token


@auth_router.get("/users/me")
async def auth_user_check_self_info(
    user: UserSchema = Depends(get_current_active_auth_user),
):
    return {
        "username": user.username,
        "email": user.email,
    }
