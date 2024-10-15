from datetime import datetime, timezone

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import models, exceptions


class AuthService:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_or_update_auth_code(
        self, phone_number: str, code: str, expiry: datetime
    ):
        existing_code = await self.db.execute(
            select(models.AuthCode).where(models.AuthCode.phone_number == phone_number)
        )
        existing_code = existing_code.scalars().first()

        if existing_code:
            await self.db.execute(
                update(models.AuthCode)
                .where(models.AuthCode.id == existing_code.id)
                .values(code=code, expiry=expiry)
            )
        else:
            new_code = models.AuthCode(
                phone_number=phone_number, code=code, expiry=expiry
            )
            self.db.add(new_code)

        await self.db.commit()

    async def verify_auth_code(self, phone_number: str, code: str):
        db_code = await self.db.execute(
            select(models.AuthCode).where(models.AuthCode.phone_number == phone_number)
        )
        db_code = db_code.scalars().first()

        if not db_code or db_code.code != code:
            raise exceptions.InvalidAuthCode

        if db_code.expiry < datetime.now(tz=timezone.utc):
            await self.db.execute(
                delete(models.AuthCode).where(models.AuthCode.id == db_code.id)
            )
            raise exceptions.AuthCodeExpired

        user_query = await self.db.execute(
            select(models.User).where(models.User.phone_number == phone_number)
        )
        user = user_query.scalars().first()

        if not user:
            user = models.User(phone_number=phone_number)
            self.db.add(user)
            await self.db.commit()

        await self.db.execute(
            delete(models.AuthCode).where(models.AuthCode.id == db_code.id)
        )
        await self.db.commit()
        return user
