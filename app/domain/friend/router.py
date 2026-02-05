from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.common.schemas import BaseResponse
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.domain.friend.schemas import FriendCreate, FriendListResponse, FriendResponse
from app.domain.friend.service import FriendService
from app.domain.wishlist.schemas import WishlistItemResponse
from app.domain.wishlist.service import WishlistService

# 친구 API 라우터
router = APIRouter()
service = FriendService()
wishlist_service = WishlistService()


def get_current_user_id(x_user_id: int | None = Header(default=None)) -> int:
    if x_user_id is None:
        raise UnauthorizedException(message="X-User-Id header is required")
    return x_user_id


@router.post("", response_model=BaseResponse[FriendResponse])
# 친구 추가
def add_friend(
    payload: FriendCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    friend = service.add_friend(
        db, owner_user_id=user_id, friend_user_id=payload.friend_user_id
    )
    return BaseResponse.ok(FriendResponse.model_validate(friend))


@router.delete("/{friend_user_id}", response_model=BaseResponse[None])
# 친구 삭제
def remove_friend(
    friend_user_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service.remove_friend(db, owner_user_id=user_id, friend_user_id=friend_user_id)
    return BaseResponse.ok(None, message="Friend removed")


@router.get("", response_model=BaseResponse[FriendListResponse])
# 친구 목록 (페이지네이션)
def list_friends(
    page: int = 1,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    data = service.list_friends(db, owner_user_id=user_id, page=page, size=10)
    return BaseResponse.ok(data)


@router.get("/{friend_user_id}/wishlist", response_model=BaseResponse[List[WishlistItemResponse]])
# 친구 위시리스트 조회
def get_friend_wishlist(
    friend_user_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    items = wishlist_service.list_friend_wishlist(
        db, requester_id=user_id, friend_user_id=friend_user_id
    )
    return BaseResponse.ok(items)
