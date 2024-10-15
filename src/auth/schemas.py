from pydantic import BaseModel


class AuthCodeRequest(BaseModel):
    phone_number: str


class AuthCodeVerifyRequest(BaseModel):
    phone_number: str
    code: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
