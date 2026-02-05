# 1. 표준 라이브러리
from typing import Any

# 2. 서드파티 라이브러리
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# 3. 로컬 모듈
from app.core.database import get_db
from app.common.schemas import BaseResponse  # 공통 응답 규격
from app.domain.user.service import UserService
from app.domain.user.schemas import UserCreate, UserResponse, UserLogin, LoginResponse

router = APIRouter()

# 템플릿의 의존성 주입 방식 준수
def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post(
    "", 
    response_model=BaseResponse[UserResponse], 
    status_code=status.HTTP_201_CREATED
)
async def signup(
    data: UserCreate, 
    service: UserService = Depends(get_service)
) -> Any:
    """
    회원가입 API
    - BaseResponse.ok를 사용하여 팀의 공통 응답 형식을 준수합니다.
    """
    # 서비스 계층에서 발생할 수 있는 ValueError 등은 
    # 관례상 전역 예외 처리기(Exception Handler)에서 처리하는 것이 템플릿의 지향점입니다.
    new_user = service.create(data)
    
    return BaseResponse.ok(
        data=UserResponse.model_validate(new_user), 
        message="회원가입이 완료되었습니다."
    )

@router.post(
    "/login",
    response_model=BaseResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="이메일과 비밀번호로 로그인합니다. 성공 시 user_id를 반환합니다.",
)
async def login(
    data: UserLogin,
    service: UserService = Depends(get_service),
) -> Any:
    """
    로그인 API
    - 이메일/비밀번호 검증 후 user_id 반환
    - 비밀번호는 Argon2로 검증
    """
    result = service.login(data)
    return BaseResponse.ok(data=LoginResponse(**result), message="로그인 성공")
