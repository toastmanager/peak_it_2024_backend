import string
import random
from datetime import datetime, timedelta, timezone
import uuid

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


def create_refresh_token():
    return str(uuid.uuid4())


def create_token_pair(user_id: uuid.UUID):
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token()
    return {"access_token": access_token, "refresh_token": refresh_token}
