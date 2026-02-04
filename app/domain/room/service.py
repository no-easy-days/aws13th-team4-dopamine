from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.domain.friend.repository import FriendRepository
from app.domain.room.models import Room
from app.domain.room.repository import RoomRepository, RoomParticipantRepository
from app.domain.room.schemas import RoomCreate, RoomDetailResponse, RoomResponse, ParticipantResponse
from app.domain.wishlist.models import WishlistItem


class RoomService:
    def __init__(
        self,
        room_repository: RoomRepository | None = None,
        participant_repository: RoomParticipantRepository | None = None,
        friend_repository: FriendRepository | None = None,
    ) -> None:
        self.room_repository = room_repository or RoomRepository()
        self.participant_repository = participant_repository or RoomParticipantRepository()
        self.friend_repository = friend_repository or FriendRepository()

    def create_room(self, db: Session, user_id: int, payload: RoomCreate) -> RoomResponse:
        """위시리스트 아이템으로 방 생성"""
        # 위시리스트 아이템 확인
        wishlist_item = db.query(WishlistItem).filter(
            WishlistItem.id == payload.wishlist_item_id,
            WishlistItem.user_id == user_id,
        ).first()

        if not wishlist_item:
            raise NotFoundException(message="Wishlist item not found")

        # 방 생성
        room = self.room_repository.create(
            db,
            room_type="WISHLIST_GIFT",
            title=payload.title,
            max_participants=payload.max_participants,
            owner_user_id=user_id,
            product_id=wishlist_item.product_id,
            gift_owner_user_id=user_id,
        )

        response = RoomResponse.model_validate(room)
        response.current_participant_count = 0
        return response

    def get_room_detail(self, db: Session, user_id: int, room_id: int) -> RoomDetailResponse:
        """방 상세 조회 (입장 화면)"""
        room = self.room_repository.get_by_id(db, room_id)
        if not room:
            raise NotFoundException(message="Room not found")

        if room.status == "DELETED":
            raise NotFoundException(message="Room not found")

        # 방장이거나 친구인지 확인
        is_owner = room.owner_user_id == user_id
        is_friend = self.friend_repository.get_by_owner_and_friend(
            db, owner_user_id=user_id, friend_user_id=room.gift_owner_user_id
        )

        if not is_owner and not is_friend:
            raise ForbiddenException(message="Not authorized to view this room")

        # 참여자 목록
        participants = self.participant_repository.list_by_room(db, room_id, state="JOINED")

        response = RoomDetailResponse.model_validate(room)
        response.participants = [ParticipantResponse.model_validate(p) for p in participants]
        response.current_participant_count = len(participants)
        response.current_ready_count = self.participant_repository.count_ready(db, room_id)

        return response

    def _to_room_response(self, db: Session, room: Room) -> RoomResponse:
        """Room 객체를 RoomResponse로 변환 (참여자 수 포함)"""
        response = RoomResponse.model_validate(room)
        response.current_participant_count = self.participant_repository.count_joined(db, room.id)
        return response

    def list_my_rooms(self, db: Session, user_id: int) -> List[RoomResponse]:
        """내가 만든 방 목록"""
        rooms = self.room_repository.list_by_gift_owner(db, user_id)
        return [self._to_room_response(db, room) for room in rooms]

    def list_friend_rooms(self, db: Session, user_id: int) -> List[RoomResponse]:
        """친구들의 OPEN 상태 방 목록"""
        # 내 친구 목록 가져오기
        friends = self.friend_repository.list_by_owner(db, user_id)
        friend_user_ids = [f.friend_user_id for f in friends]

        if not friend_user_ids:
            return []

        rooms = self.room_repository.list_open_rooms_for_friend(db, friend_user_ids)
        return [self._to_room_response(db, room) for room in rooms]

    def delete_room(self, db: Session, user_id: int, room_id: int) -> None:
        """방 삭제 (방장만 가능)"""
        room = self.room_repository.get_by_id(db, room_id)
        if not room:
            raise NotFoundException(message="Room not found")

        if room.owner_user_id != user_id:
            raise ForbiddenException(message="Only the owner can delete the room")

        if room.status == "RUNNING":
            raise BadRequestException(message="Cannot delete a running room")

        self.room_repository.soft_delete(db, room)
