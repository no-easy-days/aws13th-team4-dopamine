from typing import TypeVar, Generic, List, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    """Pagination request parameters"""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size


class PageMeta(BaseModel):
    """Pagination metadata"""

    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    total_items: int = Field(description="Total number of items")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")

    @classmethod
    def create(cls, page: int, size: int, total_items: int) -> "PageMeta":
        total_pages = (total_items + size - 1) // size if size > 0 else 0
        return cls(
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


class PagedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""

    success: bool = True
    message: str = "Success"
    data: List[T]
    meta: PageMeta


class BaseResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""

    success: bool = True
    message: str = "Success"
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: T = None, message: str = "Success") -> "BaseResponse[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str = "Failed", data: T = None) -> "BaseResponse[T]":
        return cls(success=False, message=message, data=data)


class ErrorResponse(BaseModel):
    """Error response structure"""

    success: bool = False
    code: str
    message: str
    detail: Optional[Any] = None
    data: None = None
