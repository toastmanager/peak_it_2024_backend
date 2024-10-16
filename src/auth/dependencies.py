from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.config import SECRET_AUTH
from src.auth.utils import ALGORITHM
from src.auth.service import AuthService
from src.database import get_async_session


async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    yield AuthService(session)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/verify_code")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_AUTH, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")  # type: ignore
        if phone_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return phone_number
