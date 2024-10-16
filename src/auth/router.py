from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta, timezone

from src.auth.dependencies import get_auth_service
from src.auth.schemas import (
    AuthCodeRequest,
    AuthCodeVerifyRequest,
    AuthTokenResponse,
    TokenPairResponse,
    TokenRefreshRequest,
)
from src.auth.service import AuthService
from src.auth import exceptions, constants
from src.auth.utils import create_token_pair, generate_auth_code


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request_code", status_code=status.HTTP_200_OK)
async def request_auth_code(
    request: AuthCodeRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    code = generate_auth_code(constants.AUTH_CODE_LENGTH)
    expiry = datetime.now(tz=timezone.utc) + timedelta(
        seconds=constants.AUTH_CODE_EXPIRY_SECONDS
    )
    await auth_service.create_or_update_auth_code(request.phone_number, code, expiry)

    print(f"Sended code: {code} to {request.phone_number}")

    return {"message": "Code sent successfully"}


@router.post("/verify_code", response_model=AuthTokenResponse)
async def verify_auth_code(
    request: AuthCodeVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.verify_auth_code(request.phone_number, request.code)
    except exceptions.InvalidAuthCode:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code"
        )
    except exceptions.AuthCodeExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Code expired"
        )

    tokens = create_token_pair(user.id)
    refresh_token_db = await auth_service.create_refresh_token(user.id)
    tokens["refresh_token"] = refresh_token_db
    return {**tokens, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        new_tokens = await auth_service.refresh_access_token(request.refresh_token)
    except exceptions.InvalidAuthCode:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    return {**new_tokens, "token_type": "bearer"}
