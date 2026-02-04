from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.common.schemas import BaseResponse
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.domain.room.schemas import RoomCreate, RoomResponse, RoomDetailResponse, ParticipantResponse, ReadyRequest, ReadyResponse, GameResultInfo
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


@router.get("/friends/{friend_user_id}", response_model=BaseResponse[List[RoomResponse]])
def list_rooms_by_friend(
    friend_user_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """특정 친구의 OPEN 상태 방 목록"""
    rooms = service.list_rooms_by_friend(db, user_id=user_id, friend_user_id=friend_user_id)
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


@router.post("/{room_id}/join", response_model=BaseResponse[ParticipantResponse])
def join_room(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """방 입장"""
    participant = service.join_room(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(participant)


@router.patch("/{room_id}/ready", response_model=BaseResponse[ReadyResponse])
def set_ready(
    room_id: int,
    payload: ReadyRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """레디 상태 변경. 정원이 다 차면 자동으로 사다리타기 시작."""
    participant, game_result = service.set_ready(db, user_id=user_id, room_id=room_id, is_ready=payload.is_ready)

    response = ReadyResponse(
        participant=participant,
        game_started=game_result is not None,
    )

    if game_result:
        response.game_result = GameResultInfo(
            game_id=game_result.game_id,
            payer_user_id=game_result.payer_user_id,
            recipient_user_id=game_result.recipient_user_id,
            product_id=game_result.product_id,
        )

    return BaseResponse.ok(response)


@router.post("/{room_id}/leave", response_model=BaseResponse[None])
def leave_room(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """방 나가기"""
    service.leave_room(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(None, message="Left the room")


@router.delete("/{room_id}", response_model=BaseResponse[None])
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """방 삭제 (방장만 가능)"""
    service.delete_room(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(None, message="Room deleted")
