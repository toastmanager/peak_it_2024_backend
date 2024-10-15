from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    from src.auth.models import User

    yield SQLAlchemyUserDatabase(session, User)


async def get_auth_service(session: AsyncSession = Depends(get_async_session)):
    from src.auth.service import AuthService

    yield AuthService(session)


async def get_user_manager(user_db=Depends(get_user_db)):
    from src.auth.manager import UserManager

    yield UserManager(user_db)
