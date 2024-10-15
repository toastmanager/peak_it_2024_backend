import string
import random
from datetime import datetime, timedelta, timezone

from jose import jwt

from src.config import SECRET_AUTH
from src.auth.constants import AUTH_CODE_EXPIRY_SECONDS

ALGORITHM = "HS256"


def generate_auth_code(length: int):
    return "".join(random.choices(string.digits, k=length))


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(seconds=AUTH_CODE_EXPIRY_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_AUTH, algorithm=ALGORITHM)
    return encoded_jwt
