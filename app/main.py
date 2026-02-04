from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import BaseAPIException, api_exception_handler

# Import domain routers here
# from app.domain.user.router import router as user_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS middleware
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

    # Register routers
    # app.include_router(user_router, prefix="/api/v1/users", tags=["users"])

    return app


app = create_app()
