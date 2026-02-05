from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import decode_token, create_access_token
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.common.schemas import BaseResponse
from app.domain.user.service import UserService
from app.domain.user.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post(
    "",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    data: UserCreate,
    service: UserService = Depends(get_service),
) -> Any:
    new_user = service.create(data)
    return BaseResponse.ok(
        data=UserResponse.model_validate(new_user),
        message="Signup successful",
    )


@router.post(
    "/login",
    response_model=BaseResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Authenticate with email and password and return an access token.",
)
async def login(
    data: UserLogin,
    service: UserService = Depends(get_service),
) -> Any:
    result = service.login(data)
    return BaseResponse.ok(data=LoginResponse(**result), message="Login successful")


@router.post(
    "/refresh",
    response_model=BaseResponse[TokenRefreshResponse],
    status_code=status.HTTP_200_OK,
    summary="Refresh Token",
    description="Issue a new access token using a refresh token.",
)
async def refresh_token(payload: TokenRefreshRequest) -> Any:
    token_payload = decode_token(payload.refresh_token)
    if token_payload.get("type") != "refresh":
        raise UnauthorizedException(message="Invalid token type")

    subject = token_payload.get("sub")
    if subject is None:
        raise UnauthorizedException(message="Invalid token payload")

    access_token = create_access_token(subject=str(subject))
    response = TokenRefreshResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return BaseResponse.ok(data=response, message="Token refreshed")


@router.post(
    "/logout",
    response_model=BaseResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Logout endpoint placeholder.",
)
async def logout(
    service: UserService = Depends(get_service),
) -> Any:
    service.logout()
    return BaseResponse.ok(data=None, message="Logout successful")
