from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.model = User
        self.session = session

    async def get_user_by_phone(self, phone: str) -> User:
        stmt = select(self.model).where(self.model.phone == phone)
        res = (await self.session.execute(stmt)).scalar_one_or_none()
        return res