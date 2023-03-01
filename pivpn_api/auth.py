import os
import secrets

from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def check_credentials(credentials: HTTPBasicCredentials) -> bool:
    correct_username = secrets.compare_digest(
        credentials.username,
        os.getenv("API_LOGIN", "admin"),
    )
    correct_password = secrets.compare_digest(
        credentials.password,
        os.getenv("API_PASSWORD", "admin"),
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True
