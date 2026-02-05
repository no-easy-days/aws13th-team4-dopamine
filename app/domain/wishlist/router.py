from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.schemas import BaseResponse
from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.domain.wishlist.schemas import WishlistCreate, WishlistItemResponse
from app.domain.wishlist.service import WishlistService

router = APIRouter()
service = WishlistService()


@router.get(
    "",
    response_model=BaseResponse[List[WishlistItemResponse]],
    summary="내 위시리스트 조회",
    description="로그인한 사용자의 위시리스트 전체 목록을 조회합니다.",
)
def list_my_wishlist(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    items = service.list_my_wishlist(db, user_id=user_id)
    return BaseResponse.ok(items)


@router.post(
    "",
    response_model=BaseResponse[WishlistItemResponse],
    summary="위시리스트 추가",
    description="상품을 내 위시리스트에 추가합니다. 이미 추가된 상품은 중복 추가할 수 없습니다.",
)
def add_to_wishlist(
    payload: WishlistCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    item = service.add_to_wishlist(db, user_id=user_id, payload=payload)
    return BaseResponse.ok(item)


@router.delete(
    "/{product_id}",
    response_model=BaseResponse[None],
    summary="위시리스트 삭제",
    description="위시리스트에서 특정 상품을 삭제합니다.",
)
def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service.remove_from_wishlist(db, user_id=user_id, product_id=product_id)
    return BaseResponse.ok(None, message="Wishlist item removed")
