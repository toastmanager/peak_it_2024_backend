import random
import string
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

import src.auth.exceptions as auth_exc
from src.core.config import settings


def jwt_encode(
    payload: dict,
    key: str = settings.auth.secret,
    algorithm: str = settings.auth.algorithm,
    expire_timedelta: timedelta | None = None,
    expire_seconds: int = settings.auth.access_token_expire_seconds,
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(seconds=expire_seconds)
    to_encode.update(exp=expire, iat=now, jti=uuid.uuid4().hex)
    encoded = jwt.encode(payload=to_encode, key=key, algorithm=algorithm)
    return encoded


def jwt_decode(
    token: str,
    key: str = settings.auth.secret,
    algorithm: str = settings.auth.algorithm,
):
    decoded = jwt.decode(jwt=token, key=key, algorithms=[algorithm])
    return decoded


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_seconds=settings.auth.access_token_expire_seconds,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {"type": token_type}
    jwt_payload.update(token_data)
    return jwt_encode(
        payload=jwt_payload,
        expire_seconds=expire_seconds,
        expire_timedelta=expire_timedelta,
    )


def hash_password(
    password: str,
) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt).decode()


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password=password.encode(), hashed_password=bytes(hashed_password, "utf-8")
    )


def validate_token_type(
    payload: dict,
    expected_type,
):
    token_type: str | None = payload.get("type")
    if token_type != expected_type:
        raise auth_exc.invalid_token_type(
            received_type=token_type if token_type is not None else "",
            expected_type=expected_type,
        )

def generate_auth_code(length: int):
    return "".join(random.choices(string.digits, k=length))