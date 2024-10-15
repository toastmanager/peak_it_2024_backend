import random
import string

from jose import jwt

from src.config import SECRET_AUTH

ALGORITHM = "HS256"


def generate_auth_code(length: int):
    return "".join(random.choices(string.digits, k=length))


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_AUTH, algorithm=ALGORITHM)
    return encoded_jwt
