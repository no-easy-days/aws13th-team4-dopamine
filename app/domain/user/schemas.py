import re
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, SecretStr


# =============================================================================
# [Request Schema] 클라이언트가 서버로 보낼 때 (회원가입 요청)
# 역할: 입력 데이터 검증(Validation) & 정제(Sanitization)
# =============================================================================
class UserCreate(BaseModel):
    """
    회원가입 요청 데이터 검증 모델
    """

    # 1. 이메일 검증 (EmailStr)
    # - 라이브러리가 자동으로 '@' 존재 여부, 도메인 형식을 검사합니다.
    # - 형식이 틀리면 비즈니스 로직 진입 전에 422 에러를 반환합니다.
    email: EmailStr = Field(..., description="사용자 이메일")

    # 2. 비밀번호 보안 (SecretStr + 길이 제한)py
    # - SecretStr: 로그 파일이나 print() 출력 시 '**********'로 마스킹되어 PII(개인정보) 유출을 막습니다.
    # - min=8: 무차별 대입 공격(Brute Force) 방어용 최소 길이
    # - max=50: 해싱 연산 과부하(DoS) 방지용 최대 길이
    password: SecretStr = Field(..., min_length=8, max_length=50, description="비밀번호")

    # 3. 닉네임 길이 제한
    nickname: str = Field(..., min_length=2, max_length=30, description="닉네임")

    # -------------------------------------------------------------------------
    # [Validator 1] 공백 자동 제거 (Pre-processing)
    # mode='before': Pydantic의 기본 타입 검사가 실행되기 '전'에 먼저 실행됩니다.
    # 역할: 사용자가 실수로 넣은 앞뒤 공백(" user ")을 제거("user")하여 데이터 일관성을 유지합니다.
    # -------------------------------------------------------------------------
    @field_validator('email', 'nickname', mode='before')
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    # -------------------------------------------------------------------------
    # [Validator 2] 닉네임 보안 검증 (Security Policy)
    # 역할: XSS 공격, 특수문자 깨짐, 관리자 사칭을 방지합니다.
    # -------------------------------------------------------------------------
    @field_validator('nickname')
    @classmethod
    def validate_nickname(cls, v):
        # A. 화이트리스트 검사 (허용된 문자만 통과)
        # 한글(가-힣), 영문(a-z, A-Z), 숫자(0-9)가 아니면 에러 발생
        if not re.match(r"^[가-힣a-zA-Z0-9]+$", v):
            raise ValueError("닉네임은 한글, 영문, 숫자만 사용할 수 있습니다.")

        # B. 블랙리스트 검사 (관리자 사칭 방지)
        # 시스템 중요 키워드를 닉네임으로 쓰지 못하게 막습니다.
        reserved_names = ["admin", "administrator", "root", "system", "master", "운영자", "관리자"]
        if v.lower() in reserved_names:
            raise ValueError("해당 닉네임은 사용할 수 없습니다.")

        return v


# =============================================================================
# [Response Schema] 서버가 클라이언트로 보낼 때 (응답)
# 역할: 민감 정보 필터링 & 데이터 직렬화(Serialization)
# =============================================================================
class UserResponse(BaseModel):
    """
    회원가입 성공 시 반환할 데이터 모델
    """

    id: int
    email: EmailStr
    nickname: str
    created_at: datetime

    # [보안 핵심] password 필드가 아예 존재하지 않습니다.
    # 실수로 User 객체를 통째로 리턴해도 비밀번호는 절대 외부로 나가지 않습니다.

    # [설정] ORM 모드 활성화
    # SQLAlchemy 객체(DB 모델)를 Pydantic 모델(JSON)로 변환할 수 있게 해줍니다.
    model_config = {"from_attributes": True}
