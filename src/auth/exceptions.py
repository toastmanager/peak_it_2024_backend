from fastapi import HTTPException, status

unauthenticated = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password"
)

not_found = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
)

inactive = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user inactive")

invalid_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
)


def invalid_token_type(received_type: str, expected_type: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invaild token type '{received_type}', expected '{expected_type}'",
    )

failed_to_create = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to create user"
)

no_matching_auth_code = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="matching authorization code was not found"
)

expired_auth_code = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="provided auth code is expired"
)

wrong_phone = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,  detail="wrong phone number"
)