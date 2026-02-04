from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import BaseAPIException, api_exception_handler

# 1단계: 작성하신 user 도메인의 라우터를 가져옵니다.
# 주석을 해제하여 활성화하세요.
from app.domain.user.router import router as user_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS middleware (중략)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(BaseAPIException, api_exception_handler)

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    # 2단계: 가져온 user_router를 실제 서비스 경로에 등록합니다.
    # 주석을 해제하세요. 가이드에 따라 prefix와 tags를 설정합니다.



app = create_app()