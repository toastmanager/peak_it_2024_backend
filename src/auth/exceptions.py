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


already_exist_email = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="user with that email already exists"
)

already_exist_username = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="user with that username already exists",
)

failed_to_create = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to create user"
)
