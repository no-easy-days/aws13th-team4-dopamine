from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.schemas import BaseResponse
from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.domain.friend.schemas import FriendCreate, FriendListResponse, FriendResponse
from app.domain.friend.service import FriendService
from app.domain.wishlist.schemas import WishlistItemResponse
from app.domain.wishlist.service import WishlistService

# 친구 API 라우터
router = APIRouter()
service = FriendService()
wishlist_service = WishlistService()


@router.post(
    "",
    response_model=BaseResponse[FriendResponse],
    summary="친구 추가",
    description="다른 사용자를 친구로 추가합니다. 친구 관계는 단방향입니다.",
)

def add_friend(
    payload: FriendCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    친구 추가 API
    - 단방향 관계: A→B 추가해도 B→A는 아님
    - 상대방의 방을 보려면 상대방을 친구로 등록해야 함
    """
    friend = service.add_friend(
        db, owner_user_id=user_id, friend_user_id=payload.friend_user_id
    )
    return BaseResponse.ok(FriendResponse.model_validate(friend))


@router.delete(
    "/{friend_user_id}",
    response_model=BaseResponse[None],
    summary="친구 삭제",
    description="친구 목록에서 특정 사용자를 삭제합니다.",
)
def remove_friend(
    friend_user_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service.remove_friend(db, owner_user_id=user_id, friend_user_id=friend_user_id)
    return BaseResponse.ok(None, message="Friend removed")


@router.get(
    "",
    response_model=BaseResponse[FriendListResponse],
    summary="친구 목록 조회",
    description="내 친구 목록을 페이지네이션하여 조회합니다. 페이지당 10명씩 반환됩니다.",
)
def list_friends(
    page: int = 1,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    data = service.list_friends(db, owner_user_id=user_id, page=page, size=10)
    return BaseResponse.ok(data)


@router.get(
    "/{friend_user_id}/wishlist",
    response_model=BaseResponse[List[WishlistItemResponse]],
    summary="친구 위시리스트 조회",
    description="친구로 등록된 사용자의 위시리스트를 조회합니다. 친구 관계가 아니면 조회할 수 없습니다.",
)
def get_friend_wishlist(
    friend_user_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    items = wishlist_service.list_friend_wishlist(
        db, requester_id=user_id, friend_user_id=friend_user_id
    )
    return BaseResponse.ok(items)
