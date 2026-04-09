from fastapi import APIRouter, HTTPException, status

from app.api.schemas.auth import TokenRequest, TokenResponse
from app.core.security import authenticate_user, issue_access_token


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse, summary="Get bearer token")
def get_token(payload: TokenRequest) -> TokenResponse:
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    return TokenResponse(access_token=issue_access_token())
