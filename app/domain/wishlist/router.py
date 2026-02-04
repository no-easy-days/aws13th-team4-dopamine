from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.common.schemas import BaseResponse
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.domain.wishlist.schemas import WishlistCreate, WishlistItemResponse
from app.domain.wishlist.service import WishlistService

router = APIRouter()
service = WishlistService()


def get_current_user_id(x_user_id: int | None = Header(default=None)) -> int:
    if x_user_id is None:
        raise UnauthorizedException(message="X-User-Id header is required")
    return x_user_id


@router.get("", response_model=BaseResponse[List[WishlistItemResponse]])
def list_my_wishlist(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    items = service.list_my_wishlist(db, user_id=user_id)
    return BaseResponse.ok(items)


@router.post("", response_model=BaseResponse[WishlistItemResponse])
def add_to_wishlist(
    payload: WishlistCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    item = service.add_to_wishlist(db, user_id=user_id, payload=payload)
    return BaseResponse.ok(item)


@router.delete("/{product_id}", response_model=BaseResponse[None])
def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service.remove_from_wishlist(db, user_id=user_id, product_id=product_id)
    return BaseResponse.ok(None, message="Wishlist item removed")
