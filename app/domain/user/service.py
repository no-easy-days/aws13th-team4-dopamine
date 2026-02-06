from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, create_refresh_token
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.domain.user import schemas
from app.domain.user.repository import UserRepository
from app.core.exceptions import UnauthorizedException
from app.core.auth import create_access_token

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def _get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create(self, user_create: schemas.UserCreate):
        if self.user_repo.get_by_email(user_create.email):
            raise ValueError("Email already registered")

        if self.user_repo.get_by_nickname(user_create.nickname):
            raise ValueError("Nickname already in use")

        hashed_password = self._get_password_hash(user_create.password.get_secret_value())
        return self.user_repo.create(user_create=user_create, hashed_password=hashed_password)

    def login(self, user_login: schemas.UserLogin):
        """
        [로그인]
        1. 이메일로 사용자 조회
        2. 비밀번호 검증
        3. JWT 토큰 발급
        """
        user = self.user_repo.get_by_email(user_login.email)
        if not user:
            raise UnauthorizedException(message="Invalid credentials")

        if not pwd_context.verify(user_login.password.get_secret_value(), user.password_hash):
            raise UnauthorizedException(message="Invalid credentials")

        # JWT 토큰 생성
        access_token = create_access_token(user_id=user.id, email=user.email)

        return {
            "user_id": user.id,
            "access_token": access_token,
            "token_type": "bearer"
        }

    def logout(self):
        pass
