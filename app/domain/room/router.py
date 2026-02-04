from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.common.schemas import BaseResponse
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.domain.room.schemas import RoomCreate, RoomResponse, RoomDetailResponse
from app.domain.room.service import RoomService

router = APIRouter()
service = RoomService()


def get_current_user_id(x_user_id: int | None = Header(default=None)) -> int:
    if x_user_id is None:
        raise UnauthorizedException(message="X-User-Id header is required")
    return x_user_id


@router.post("", response_model=BaseResponse[RoomResponse])
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """위시리스트 아이템으로 방 생성"""
    room = service.create_room(db, user_id=user_id, payload=payload)
    return BaseResponse.ok(room)


@router.get("/my", response_model=BaseResponse[List[RoomResponse]])
def list_my_rooms(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """내가 만든 방 목록"""
    rooms = service.list_my_rooms(db, user_id=user_id)
    return BaseResponse.ok(rooms)


@router.get("/friends", response_model=BaseResponse[List[RoomResponse]])
def list_friend_rooms(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """친구들의 OPEN 상태 방 목록"""
    rooms = service.list_friend_rooms(db, user_id=user_id)
    return BaseResponse.ok(rooms)


@router.get("/{room_id}", response_model=BaseResponse[RoomDetailResponse])
def get_room_detail(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """방 상세 조회 (입장)"""
    room = service.get_room_detail(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(room)


@router.delete("/{room_id}", response_model=BaseResponse[None])
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """방 삭제 (방장만 가능)"""
    service.delete_room(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(None, message="Room deleted")
