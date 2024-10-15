from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import models, exceptions
from src.auth.constants import REFRESH_TOKEN_EXPIRE_DAYS
from src.auth.utils import create_token_pair


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

    async def create_refresh_token(self, user_id: uuid.UUID):
        expiry = datetime.now(tz=timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
        refresh_token = models.RefreshToken(user_id=user_id, expiry=expiry)
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token.token

    async def refresh_access_token(self, refresh_token: str):
        db_refresh_token = await self.db.execute(
            select(models.RefreshToken)
            .where(models.RefreshToken.token == refresh_token)
            .where(models.RefreshToken.revoked == False)  # noqa: E712
        )
        db_refresh_token = db_refresh_token.scalars().first()
        if not db_refresh_token or db_refresh_token.expiry < datetime.now(
            tz=timezone.utc
        ):
            raise exceptions.InvalidAuthCode

        user = await self.db.get(models.User, db_refresh_token.user_id)
        new_tokens = create_token_pair(user.id)  # type: ignore

        db_refresh_token.token = new_tokens["refresh_token"]
        db_refresh_token.expiry = datetime.now(tz=timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.db.commit()

        return new_tokens

    async def revoke_refresh_token(self, refresh_token: str):
        db_refresh_token = await self.db.execute(
            select(models.RefreshToken).where(
                models.RefreshToken.token == refresh_token
            )
        )
        db_refresh_token = db_refresh_token.scalars().first()
        if not db_refresh_token:
            raise exceptions.InvalidAuthCode
        db_refresh_token.revoked = True
        await self.db.commit()
