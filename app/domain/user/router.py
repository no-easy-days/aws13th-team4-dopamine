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
    description="이메일과 비밀번호로 로그인합니다. 성공 시 JWT 액세스 토큰을 반환합니다.",
)
async def login(
        data: UserLogin,
        service: UserService = Depends(get_service),
) -> Any:
    """
    로그인 API
    - 이메일/비밀번호 검증 후 user_id 반환
    """
    result = service.login(data)
    return BaseResponse.ok(data=LoginResponse(**result), message="로그인 성공")


@router.post(
    "/logout",
    response_model=BaseResponse[None],
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
    description="로그아웃을 처리합니다.",
)
async def logout(
        service: UserService = Depends(get_service)
) -> Any:
    """
    로그아웃 API
    - 서버의 상태를 변경하지 않고 성공 응답을 반환하여 클라이언트의 토큰 파기를 유도합니다.
    """
    service.logout()  # 서비스 계층의 빈 로직 호출
    return BaseResponse.ok(data=None, message="성공적으로 로그아웃되었습니다.")