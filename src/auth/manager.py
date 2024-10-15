import uuid

from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users import exceptions

from src.auth.schemas import UserCreate
from src.config import SECRET
from src.auth.models import User
from src.auth.service import AuthService
from src.database import async_session_maker


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {
              user.id}. Verification token: {token}")

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Request | None = None,
    ) -> User:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        async with async_session_maker() as session:
            auth_service = AuthService(session)

            await self.validate_password(user_create.password, user_create)

            existing_user = await auth_service.get_user_by_phone(user_create.phone)
            if existing_user is not None:
                raise exceptions.UserAlreadyExists()

            user_dict = (
                user_create.create_update_dict()
                if safe
                else user_create.create_update_dict_superuser()
            )
            password = user_dict.pop("password")
            user_dict["hashed_password"] = self.password_helper.hash(password)

            created_user = await self.user_db.create(user_dict)

            await self.on_after_register(created_user, request)

            return created_user

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> User | None:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
        async with async_session_maker() as session:
            auth_service = AuthService(session)

            try:
                user = await auth_service.get_user_by_phone(credentials.username)
            except exceptions.UserNotExists:
                # Run the hasher to mitigate timing attack
                # Inspired from Django: https://code.djangoproject.com/ticket/20760
                self.password_helper.hash(credentials.password)
                return None

            verified, updated_password_hash = self.password_helper.verify_and_update(
                credentials.password, user.hashed_password
            )
            if not verified:
                return None
            # Update password hash to a more robust one if needed
            if updated_password_hash is not None:
                await self.user_db.update(
                    user, {"hashed_password": updated_password_hash}
                )

            return user
