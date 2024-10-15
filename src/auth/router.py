from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta, timezone

from src.auth.dependencies import get_auth_service
from src.auth.schemas import AuthCodeRequest, AuthCodeVerifyRequest, AuthTokenResponse
from src.auth.service import AuthService
from src.auth import exceptions, constants
from src.auth.utils import generate_auth_code, create_access_token


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

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
