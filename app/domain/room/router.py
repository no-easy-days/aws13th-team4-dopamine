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


@router.post(
    "",
    response_model=BaseResponse[RoomResponse],
    summary="방 생성",
    description="위시리스트에 등록된 상품으로 사다리타기 방을 생성합니다. WISHLIST_GIFT 타입은 친구들이 참여하여 당첨자가 방장에게 선물을 사주고, PRODUCT_LADDER 타입은 참여자 중 당첨자가 선물을 받습니다.",
)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    room = service.create_room(db, user_id=user_id, payload=payload)
    return BaseResponse.ok(room)


@router.get(
    "/my",
    response_model=BaseResponse[List[RoomResponse]],
    summary="내 방 목록 조회",
    description="내가 생성한 모든 방 목록을 조회합니다. 상태(OPEN/DONE)와 관계없이 모든 방을 반환합니다.",
)
def list_my_rooms(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    rooms = service.list_my_rooms(db, user_id=user_id)
    return BaseResponse.ok(rooms)


@router.get(
    "/friends",
    response_model=BaseResponse[List[RoomResponse]],
    summary="친구들 방 목록 조회",
    description="내가 친구로 등록한 사용자들의 OPEN 상태 방 목록을 조회합니다. 친구 관계는 단방향이므로 내가 친구로 등록한 사람의 방만 볼 수 있습니다.",
)
def list_friend_rooms(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    rooms = service.list_friend_rooms(db, user_id=user_id)
    return BaseResponse.ok(rooms)


@router.get(
    "/friends/{friend_user_id}",
    response_model=BaseResponse[List[RoomResponse]],
    summary="특정 친구 방 목록 조회",
    description="특정 친구의 OPEN 상태 방 목록을 조회합니다. 해당 사용자를 친구로 등록한 상태여야 합니다.",
)
def list_rooms_by_friend(
    friend_user_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    rooms = service.list_rooms_by_friend(db, user_id=user_id, friend_user_id=friend_user_id)
    return BaseResponse.ok(rooms)


@router.get(
    "/{room_id}",
    response_model=BaseResponse[RoomDetailResponse],
    summary="방 상세 조회",
    description="방의 상세 정보와 참여자 목록을 조회합니다. 방장의 친구이거나 PRODUCT_LADDER 타입인 경우 조회할 수 있습니다.",
)
def get_room_detail(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    room = service.get_room_detail(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(room)


@router.post(
    "/{room_id}/join",
    response_model=BaseResponse[ParticipantResponse],
    summary="방 입장",
    description="방에 참여합니다. WISHLIST_GIFT 타입은 친구만 입장 가능하며 방장은 입장 불가, PRODUCT_LADDER 타입은 방장 포함 누구나 입장 가능합니다. 이전에 나갔던 방에 다시 입장할 수 있습니다.",
)
def join_room(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    participant = service.join_room(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(participant)


@router.patch(
    "/{room_id}/ready",
    response_model=BaseResponse[ReadyResponse],
    summary="레디 상태 변경",
    description="참여자의 레디 상태를 변경합니다. 모든 참여자가 레디하여 정원이 차면 자동으로 사다리타기 게임이 시작되고 결과가 반환됩니다. 동시성 이슈를 방지하기 위해 비관적 락이 적용되어 있습니다.",
)
def set_ready(
    room_id: int,
    payload: ReadyRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
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


@router.post(
    "/{room_id}/leave",
    response_model=BaseResponse[None],
    summary="방 나가기",
    description="방에서 나갑니다. 레디 상태와 관계없이 나갈 수 있으며, 나간 후에도 다시 입장할 수 있습니다. 방장은 방을 나갈 수 없고 삭제만 가능합니다.",
)
def leave_room(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service.leave_room(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(None, message="Left the room")


@router.delete(
    "/{room_id}",
    response_model=BaseResponse[None],
    summary="방 삭제",
    description="방을 삭제합니다. 방장만 삭제할 수 있으며, OPEN 상태인 방만 삭제 가능합니다.",
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service.delete_room(db, user_id=user_id, room_id=room_id)
    return BaseResponse.ok(None, message="Room deleted")
