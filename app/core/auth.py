"""
JWT 기반 인증 모듈
"""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Header

from app.core.config import settings
from app.core.exceptions import UnauthorizedException

# JWT 설정
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = settings.JWT_EXPIRE_HOURS

# 시크릿 키 검증 (빈 값이면 경고)
if not JWT_SECRET_KEY:
    import warnings
    warnings.warn("JWT_SECRET_KEY is not set! Please set it in .env file for production.")


def create_access_token(user_id: int, email: str) -> str:
    """JWT 액세스 토큰 생성"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """JWT 토큰 검증 및 페이로드 반환"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(message="Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException(message="Invalid token")


def get_current_user_id(authorization: Optional[str] = Header(default=None)) -> int:
    """
    Authorization 헤더에서 JWT 토큰을 추출하고 user_id 반환

    사용법:
    - Header: Authorization: Bearer <token>
    - 또는 하위 호환: X-User-Id: <user_id> (개발/테스트용)
    """
    if authorization is None:
        raise UnauthorizedException(message="Authorization header is required")

    # Bearer 토큰 형식 확인
    if authorization.startswith("Bearer "):
        token = authorization[7:]  # "Bearer " 제거
        payload = verify_token(token)
        return int(payload["sub"])

    # 하위 호환: 숫자만 있으면 X-User-Id처럼 처리 (개발용)
    try:
        return int(authorization)
    except ValueError:
        raise UnauthorizedException(message="Invalid authorization format. Use 'Bearer <token>'")


def get_current_user_id_optional(authorization: Optional[str] = Header(default=None)) -> Optional[int]:
    """
    선택적 인증 (인증 없어도 접근 가능한 엔드포인트용)
    """
    if authorization is None:
        return None

    try:
        return get_current_user_id(authorization)
    except UnauthorizedException:
        return None
