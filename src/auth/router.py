from fastapi import APIRouter, Depends, Form, HTTPException, status

from src.auth.dependencies import get_auth_service
from src.auth.schemas import Token, AuthCodeRequest, AuthCodeVerify
from src.auth.service import AuthService

auth_router = APIRouter(prefix="/jwt", tags=["JWT"])


@auth_router.post("/verify_code", response_model=Token)
async def verify_code(
    auth_code_verify_schema: AuthCodeVerify,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    try:
        return await auth_service.verify_code(
            auth_code_verify_schema=auth_code_verify_schema
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to verify code: " + str(e)
        )


@auth_router.post("/request_code")
async def request_code(
    auth_code_request_schema: AuthCodeRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        await auth_service.request_code(
            auth_code_request_schema=auth_code_request_schema
        )
        return {"message": "successfully sended authorization code"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request code",
        )


@auth_router.post("/refresh", response_model=Token)
async def refresh_jwt(
    refresh_token: str = Form(), auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    payload = auth_service.get_current_token_payload(refresh_token)
    token: Token = await auth_service.refresh_token(payload)
    return token
