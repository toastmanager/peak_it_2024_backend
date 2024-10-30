from datetime import datetime, timedelta, timezone
import uuid

from jwt.exceptions import InvalidTokenError

import src.auth.exceptions as auth_exc
import src.auth.utils as auth_utils
from src.auth.models import AuthCode, User
from src.auth.repositories import (
    AuthCodeRepository,
    AuthRepository,
    BlacklistTokenRepository,
)
from src.auth.schemas import AuthCodeRequest, AuthCodeVerify, Token
from src.core.config import settings


class AuthService:
    auth_repo: AuthRepository
    blacklist_token_repo: BlacklistTokenRepository
    auth_code_repo: AuthCodeRepository

    def __init__(
        self,
        users_repository: AuthRepository,
        blacklist_token_repository: BlacklistTokenRepository,
        auth_code_repository: AuthCodeRepository,
    ) -> None:
        self.auth_repo = users_repository
        self.blacklist_token_repo = blacklist_token_repository
        self.auth_code_repo = auth_code_repository

    async def request_code(self, auth_code_request_schema: AuthCodeRequest):
        auth_code_request_dict: dict = auth_code_request_schema.model_dump()
        code = auth_utils.generate_auth_code(length=settings.auth.auth_code_length)
        try:
            await self.auth_code_repo.create(
                attributes={
                    "code": code,
                    "phone": auth_code_request_dict["phone"],
                    "expiry": datetime.now(tz=timezone.utc)
                    + timedelta(seconds=settings.auth.auth_code_expire_seconds),
                }
            )
            print(code)
        except Exception as e:
            raise e

    async def verify_code(self, auth_code_verify_schema: AuthCodeVerify) -> Token:
        data = auth_code_verify_schema.model_dump()

        auth_code: AuthCode = await self.auth_code_repo.get_by(
            field="code", value=data["code"], unique=True
        )  # type: ignore
        if not auth_code:
            raise auth_exc.no_matching_auth_code
        await self.auth_code_repo.delete(auth_code)
        if auth_code.expiry < datetime.now(tz=timezone.utc):
            raise auth_exc.expired_auth_code
        if auth_code.phone != auth_code_verify_schema.phone:
            raise auth_exc.wrong_phone

        user_with_that_phone: User = await self.auth_repo.get_by(
            field="phone", value=data["phone"], unique=True
        )  # type: ignore
        if not user_with_that_phone:
            user = await self.auth_repo.create(attributes={"phone": data["phone"]})
            if not user:
                raise auth_exc.failed_to_create
        else:
            user = user_with_that_phone

        return self.create_token(user)

    async def refresh_token(self, payload: dict) -> Token:
        token_id: uuid.UUID = uuid.UUID(hex=payload.get("jti"))
        user_id: uuid.UUID = uuid.UUID(hex=payload.get("sub"))
        blacklist_token = await self.blacklist_token_repo.get_by(
            field="id", value=token_id, unique=True
        )
        if blacklist_token:
            raise auth_exc.invalid_token
        await self.blacklist_token_repo.create(
            attributes={
                "id": token_id,
                "user_id": user_id,
            }
        )
        user: User = await self.get_current_auth_user_for_refresh(payload=payload)
        return self.create_token(user)

    def create_token(self, user: User) -> Token:
        return Token(
            access_token=self.create_access_token(user),
            refresh_token=self.create_refresh_token(user),
        )

    def create_access_token(self, user: User) -> str:
        jwt_payload = {
            "sub": user.id.hex,
            "phone": user.phone,
            "superuser": user.superuser,
            "active": user.active,
        }
        return auth_utils.create_jwt(token_type="access", token_data=jwt_payload)

    def create_refresh_token(self, user: User) -> str:
        jwt_payload = {
            "sub": user.id.hex,
        }
        return auth_utils.create_jwt(
            token_type="refresh",
            token_data=jwt_payload,
            expire_timedelta=timedelta(days=settings.auth.refresh_token_expire_days),
        )

    async def get_current_active_auth_user(self, token: str) -> User:
        user: User = await self.get_current_auth_user(
            payload=self.get_current_token_payload(token=token)
        )
        if user.active:
            return user
        raise auth_exc.inactive

    async def get_current_auth_user(
        self,
        payload: dict,
    ) -> User:
        auth_utils.validate_token_type(payload, "access")
        return await self.get_user_by_token_sub(payload)

    async def get_current_auth_user_for_refresh(
        self,
        payload: dict,
    ) -> User:
        auth_utils.validate_token_type(payload, "refresh")
        return await self.get_user_by_token_sub(payload)

    async def get_user_by_token_sub(self, payload: dict) -> User:
        user_id: str | None = payload.get("sub")
        user: User = await self.auth_repo.get_by(field="id", value=user_id, unique=True)  # type: ignore
        if user:
            return user
        raise auth_exc.not_found

    def get_current_token_payload(
        self,
        token: str,
    ) -> dict:
        try:
            payload = auth_utils.jwt_decode(token=token)
        except InvalidTokenError:
            raise auth_exc.invalid_token
        return payload
