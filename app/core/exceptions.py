from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any


class BaseAPIException(Exception):
    """Base exception for API errors"""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        detail: Any = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


class NotFoundException(BaseAPIException):
    """Resource not found"""

    def __init__(self, message: str = "Resource not found", detail: Any = None):
        super().__init__(
            status_code=404,
            code="NOT_FOUND",
            message=message,
            detail=detail,
        )


class BadRequestException(BaseAPIException):
    """Bad request"""

    def __init__(self, message: str = "Bad request", detail: Any = None):
        super().__init__(
            status_code=400,
            code="BAD_REQUEST",
            message=message,
            detail=detail,
        )


class UnauthorizedException(BaseAPIException):
    """Unauthorized access"""

    def __init__(self, message: str = "Unauthorized", detail: Any = None):
        super().__init__(
            status_code=401,
            code="UNAUTHORIZED",
            message=message,
            detail=detail,
        )


class ForbiddenException(BaseAPIException):
    """Forbidden access"""

    def __init__(self, message: str = "Forbidden", detail: Any = None):
        super().__init__(
            status_code=403,
            code="FORBIDDEN",
            message=message,
            detail=detail,
        )


class ConflictException(BaseAPIException):
    """Resource conflict"""

    def __init__(self, message: str = "Conflict", detail: Any = None):
        super().__init__(
            status_code=409,
            code="CONFLICT",
            message=message,
            detail=detail,
        )


class InternalServerException(BaseAPIException):
    """Internal server error"""

    def __init__(self, message: str = "Internal server error", detail: Any = None):
        super().__init__(
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message=message,
            detail=detail,
        )


async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Global exception handler for BaseAPIException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code,
            "message": exc.message,
            "detail": exc.detail,
            "data": None,
        },
    )
