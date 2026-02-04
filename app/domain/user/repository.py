from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError  # DB 무결성 에러 감지

from app.domain.user.models import User
from app.domain.user import schemas

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_create: schemas.UserCreate, hashed_password: str) -> User:
        """
        [회원 생성]
        - 보안: **dict(언패킹)를 사용하지 않고 명시적으로 필드를 할당하여 의도치 않은 데이터 주입 방지
        - 안정성: IntegrityError 처리를 통해 동시성 이슈(따닥 클릭) 및 중복 데이터 예외 처리
        """
        try:
            # 1. 명시적 객체 생성 (Models.py의 password_hash 컬럼명)
            user = User(
                email=user_create.email,
                nickname=user_create.nickname,
                password_hash=hashed_password
            )
            
            # 2. DB 반영
            self.db.add(user)
            self.db.commit()      # 여기서 실제 저장 및 트랜잭션 종료
            self.db.refresh(user) # 생성된 ID 및 기본값 로드
            return user
            
        except IntegrityError as e:
            # 중복 가입 시 서버 터짐 방지 및 원인 파악
            self.db.rollback()
            error_msg = str(e.orig)
            
            if "email" in error_msg:
                raise ValueError("이미 사용 중인 이메일입니다.")
            elif "nickname" in error_msg:
                raise ValueError("이미 사용 중인 닉네임입니다.")
            else:
                raise ValueError("데이터베이스 저장 중 오류가 발생했습니다.") from e

    def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 회원 단건 조회 (SQLAlchemy 2.0 Style)"""
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def get_by_nickname(self, nickname: str) -> Optional[User]:
        """닉네임으로 회원 단건 조회"""
        stmt = select(User).where(User.nickname == nickname)
        return self.db.scalar(stmt)