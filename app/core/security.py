from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings


bearer_scheme = HTTPBearer(auto_error=False)



def authenticate_user(username: str, password: str) -> bool:
    settings = get_settings()
    return username == settings.api_auth_username and password == settings.api_auth_password



def issue_access_token() -> str:
    settings = get_settings()
    return settings.api_bearer_token



def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    settings = get_settings()
    if credentials.credentials != settings.api_bearer_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token.",
        )
    return credentials.credentials
