from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import AuthService
from src.database import get_async_session


async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    yield AuthService(session)
