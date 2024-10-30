from datetime import timedelta
import uuid

from jwt.exceptions import InvalidTokenError

import src.auth.exceptions as auth_exc
import src.auth.utils as auth_utils
from src.auth.models import User
from src.auth.repositories import AuthRepository, BlacklistTokenRepository
from src.auth.schemas import CreateUser, Token
from src.core.config import settings


class AuthService:
    auth_repo: AuthRepository
    blacklist_token_repo: BlacklistTokenRepository

    def __init__(
        self,
        users_repository: AuthRepository,
        blacklist_token_repository: BlacklistTokenRepository,
    ) -> None:
        self.auth_repo = users_repository
        self.blacklist_token_repo = blacklist_token_repository

    async def create_user(self, create_user_schema: CreateUser) -> Token:
        data = create_user_schema.model_dump()

        user_with_that_username = await self.auth_repo.get_by(
            field="username", value=data["username"]
        )
        user_with_that_email = await self.auth_repo.get_by(
            field="email", value=data["email"]
        )
        if user_with_that_username:
            raise auth_exc.already_exist_username
        if user_with_that_email:
            raise auth_exc.already_exist_email

        password = data.pop("password")
        data["hashed_password"] = auth_utils.hash_password(password)

        user = await self.auth_repo.create(attributes=data)
        if not user:
            raise auth_exc.failed_to_create

        return self.create_token(user)

    async def validate_auth_user(self, username: str, password: str) -> User:
        user: User = await self.auth_repo.get_by(
            field="username", value=username, unique=True
        )  # type: ignore
        if not user:
            raise auth_exc.unauthenticated

        if auth_utils.validate_password(
            password=password, hashed_password=user.hashed_password
        ):
            return user

        raise auth_exc.unauthenticated

    async def login(self, username: str, password: str) -> Token:
        user: User = await self.validate_auth_user(username=username, password=password)
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
            "username": user.username,
            "email": user.email,
            "superuser": user.superuser,
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
