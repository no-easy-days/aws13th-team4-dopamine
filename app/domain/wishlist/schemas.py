from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class WishlistProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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
    price: Optional[int] = None


class WishlistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    memo: Optional[str] = None
    priority: Optional[int] = None
    created_at: datetime
    product: Optional[WishlistProductResponse] = None


class FriendWishlistResponse(BaseModel):
    items: List[WishlistItemResponse]


class WishlistCreate(BaseModel):
    product_id: int
    memo: Optional[str] = None
    priority: Optional[int] = None
