# 1. 표준 라이브러리 (해당 파일에서는 생략 가능하나 가이드 준수)
from typing import Optional

# 2. 서드파티 라이브러리
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# 3. 로컬 모듈
from app.domain.user import schemas
from app.domain.user.repository import UserRepository
from app.core.exceptions import UnauthorizedException


# [보안 설정: Argon2]
# 인프라를 고려하는 백엔드 개발자라면 패스워드 해싱 알고리즘 선택에 신중해야 합니다.
# Argon2는 메모리 하드(Memory-hard) 방식으로, GPU를 이용한 무차별 대입 공격에 매우 강합니다.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        """의존성 주입: Repository를 생성자로 받아 내부에서 사용합니다."""
        self.user_repo = UserRepository(db)

    def _get_password_hash(self, password: str) -> str:
        """평문 비밀번호를 안전한 해시값으로 변환합니다."""
        return pwd_context.hash(password)

    def create(self, user_create: schemas.UserCreate):
        """
        [회원가입 비즈니스 로직]
        1. 이메일 및 닉네임 중복 여부를 'Fail Fast' 원칙에 따라 먼저 검사합니다.
        2. 통과 시, 보안을 위해 비밀번호를 Argon2로 해싱합니다.
        3. 준비된 데이터를 Repository에 전달하여 최종 저장합니다.
        """
        # A. 이메일 중복 체크 (Fail Fast)
        if self.user_repo.get_by_email(user_create.email):
            raise ValueError("이미 등록된 이메일입니다.")

        # B. 닉네임 중복 체크
        if self.user_repo.get_by_nickname(user_create.nickname):
            raise ValueError("이미 사용 중인 닉네임입니다.")

        # C. 비밀번호 암호화 
        # schemas.py의 SecretStr에서 실제 값을 꺼낼 때는 .get_secret_value()를 사용합니다.
        hashed_password = self._get_password_hash(user_create.password.get_secret_value())

        # D. DB 저장 요청 (Repository에 위임) 및 결과 반환
        return self.user_repo.create(user_create=user_create, hashed_password=hashed_password)

    def login(self, user_login: schemas.UserLogin):
        """
        [로그인]
        1. 이메일로 사용자 조회
        2. 비밀번호 검증
        """
        user = self.user_repo.get_by_email(user_login.email)
        if not user:
            raise UnauthorizedException(message="Invalid credentials")

        if not pwd_context.verify(user_login.password.get_secret_value(), user.password_hash):
            raise UnauthorizedException(message="Invalid credentials")

        return {"user_id": user.id}
