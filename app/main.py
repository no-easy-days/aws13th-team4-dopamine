from itertools import product

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import BaseAPIException, api_exception_handler
from app.domain.user.router import router as user_router
from app.domain.friend.router import router as friend_router
from app.domain.wishlist.router import router as wishlist_router
from app.domain.room.router import router as room_router
from app.domain.product.router import router as product_router

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
    app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(friend_router, prefix="/api/v1/friends", tags=["Friends"])
    app.include_router(wishlist_router, prefix="/api/v1/wishlist", tags=["Wishlist"])
    app.include_router(room_router, prefix="/api/v1/rooms", tags=["Rooms"])
    app.include_router(product_router)
    return app



app = create_app()
