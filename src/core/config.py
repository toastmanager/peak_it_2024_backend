import os

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv()


class DBSettings(BaseModel):
    user: str = os.environ.get("DB_USER", "")
    name: str = os.environ.get("DB_NAME", "")
    password: str = os.environ.get("DB_PASS", "")
    host: str = os.environ.get("DB_HOST", "")
    port: str = os.environ.get("DB_PORT", "")
    url: str = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AuthSettings(BaseModel):
    secret: str = os.environ.get("AUTH_SECRET", "")
    algorithm: str = os.environ.get("AUTH_ALGORITHM", "")
    access_token_expire_seconds: int = int(
        os.environ.get("ACCESS_TOKEN_EXPIRE_SECONDS", "")
    )
    refresh_token_expire_days: int = int(
        os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "")
    )


class S3Settings(BaseModel):
    access_key: str = os.environ.get("S3_ACCESS_KEY",  "")
    secrret_key: str = os.environ.get("S3_SECRET_KEY",  "")
    endpoint_url: str = os.environ.get("S3_ENDPOINT_URL",  "")

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    auth: AuthSettings = AuthSettings()
    s3: S3Settings = S3Settings()
    host: str = os.environ.get("HOST", "")


settings = Settings()
