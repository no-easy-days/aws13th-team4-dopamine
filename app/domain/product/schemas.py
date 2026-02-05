from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProductSearchItem(BaseModel):
    """Search result item"""

    source: str
    source_product_id: str
    title: str
    price: int
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    mall_name: Optional[str] = None
    brand: Optional[str] = None
    maker: Optional[str] = None
    category1: Optional[str] = None
    category2: Optional[str] = None
    category3: Optional[str] = None
    category4: Optional[str] = None

    class Config:
        from_attributes = True


class ProductDetail(BaseModel):
    """Product detail"""

    id: int
    source: str
    source_product_id: str
    title: str
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    mall_name: Optional[str] = None
    brand: Optional[str] = None
    maker: Optional[str] = None
    category1: Optional[str] = None
    category2: Optional[str] = None
    category3: Optional[str] = None
    category4: Optional[str] = None
    price: int
    last_fetched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    page: int
    size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ProductSearchResponse(BaseModel):
    """Product search response"""

    success: bool = True
    message: str = "Success"
    data: List[ProductSearchItem]
    meta: PaginationMeta


class ProductDetailResponse(BaseModel):
    """Product detail response"""

    success: bool = True
    message: str = "Success"
    data: ProductDetail


class ProductFavoriteCreate(BaseModel):
    """Save a product as a favorite"""

    source: str = Field(default="NAVER", min_length=1, max_length=20)
    source_product_id: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=255)
    image_url: Optional[str] = Field(default=None, max_length=2000)
    link_url: Optional[str] = Field(default=None, max_length=2000)
    mall_name: Optional[str] = Field(default=None, max_length=120)
    brand: Optional[str] = Field(default=None, max_length=120)
    maker: Optional[str] = Field(default=None, max_length=120)
    category1: Optional[str] = Field(default=None, max_length=120)
    category2: Optional[str] = Field(default=None, max_length=120)
    category3: Optional[str] = Field(default=None, max_length=120)
    category4: Optional[str] = Field(default=None, max_length=120)
    price: int = Field(..., ge=0)


class ProductFavoriteListResponse(BaseModel):
    """Favorite products list response"""

    success: bool = True
    message: str = "Success"
    data: List[ProductDetail]
    meta: PaginationMeta


class ProductFavoriteDeleteResponse(BaseModel):
    """Favorite product delete response"""

    success: bool = True
    message: str = "Success"
    data: None = None
