from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthCode, BlacklistToken, User
from src.auth.repositories import (
    AuthCodeRepository,
    AuthRepository,
    BlacklistTokenRepository,
)
from src.auth.service import AuthService
from src.core.dependencies import get_async_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/jwt/login/")


async def get_auth_repository(session: AsyncSession = Depends(get_async_session)):
    repository = AuthRepository(session=session, model=User)
    yield repository


async def get_blacklist_token_repository(
    session: AsyncSession = Depends(get_async_session),
):
    repository = BlacklistTokenRepository(session=session, model=BlacklistToken)
    yield repository


async def get_auth_code_repository(
    session: AsyncSession = Depends(get_async_session),
):
    repository = AuthCodeRepository(session=session, model=AuthCode)
    yield repository


async def get_auth_service(
    users_repository: AuthRepository = Depends(get_auth_repository),
    blacklist_token_repository: BlacklistTokenRepository = Depends(
        get_blacklist_token_repository
    ),
    auth_code_repository: AuthCodeRepository = Depends(get_auth_code_repository),
):
    service = AuthService(
        users_repository=users_repository,
        blacklist_token_repository=blacklist_token_repository,
        auth_code_repository=auth_code_repository,
    )
    yield service


async def get_current_active_auth_user(
    users_service: AuthService = Depends(get_auth_service),
    token: str = Depends(oauth2_scheme),
):
    user = await users_service.get_current_active_auth_user(token=token)
    yield user
