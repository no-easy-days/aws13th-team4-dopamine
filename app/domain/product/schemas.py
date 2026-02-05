from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel


class ProductSearchItem(BaseModel):
    """검색 결과"""
    title: str
    price: int
    image_url: Optional[str] = None
    mall_name: Optional[str] = None

    class Config:
        from_attributes = True

class ProductDetail(BaseModel):
    """상품 상세 정보 전체"""
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
    """상품 검색 목록 응답 """
    success: bool = True
    message: str = "Success"
    data: List[ProductSearchItem]
    meta: PaginationMeta

class ProductDetailResponse(BaseModel):
    """상품 상세 조회 응답 """
    success: bool = True
    message: str = "Success"
    data: ProductDetail