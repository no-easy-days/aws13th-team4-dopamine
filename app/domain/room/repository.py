import secrets
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.room.models import Room, RoomParticipant


class RoomRepository:
    @staticmethod
    def get_by_id(db: Session, room_id: int) -> Optional[Room]:
        return db.query(Room).filter(Room.id == room_id).first()

    @staticmethod
    def get_by_join_code(db: Session, join_code: str) -> Optional[Room]:
        return db.query(Room).filter(Room.join_code == join_code).first()

    @staticmethod
    def list_by_gift_owner(db: Session, gift_owner_user_id: int) -> List[Room]:
        return (
            db.query(Room)
            .filter(
                Room.gift_owner_user_id == gift_owner_user_id,
                Room.status != "DELETED",
            )
            .order_by(Room.created_at.desc())
            .all()
        )

    @staticmethod
    def list_open_rooms_for_friend(db: Session, friend_user_ids: List[int]) -> List[Room]:
        """친구들의 OPEN 상태 방 목록 조회"""
        return (
            db.query(Room)
            .filter(
                Room.gift_owner_user_id.in_(friend_user_ids),
                Room.status == "OPEN",
                Room.room_type == "WISHLIST_GIFT",
            )
            .order_by(Room.created_at.desc())
            .all()
        )

    @staticmethod
    def list_by_friend(db: Session, friend_user_id: int) -> List[Room]:
        """특정 친구의 OPEN 상태 방 목록 조회"""
        return (
            db.query(Room)
            .filter(
                Room.gift_owner_user_id == friend_user_id,
                Room.status == "OPEN",
                Room.room_type == "WISHLIST_GIFT",
            )
            .order_by(Room.created_at.desc())
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        room_type: str,
        title: Optional[str],
        max_participants: int,
        owner_user_id: int,
        product_id: int,
        gift_owner_user_id: int,
    ) -> Room:
        join_code = secrets.token_urlsafe(16)
        room = Room(
            room_type=room_type,
            title=title,
            status="OPEN",
            max_participants=max_participants,
            is_auto_start=True,
            join_code=join_code,
            owner_user_id=owner_user_id,
            product_id=product_id,
            gift_owner_user_id=gift_owner_user_id,
        )
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

    @staticmethod
    def update_status(db: Session, room: Room, status: str) -> Room:
        room.status = status
        db.commit()
        db.refresh(room)
        return room

    @staticmethod
    def soft_delete(db: Session, room: Room) -> Room:
        from datetime import datetime
        room.status = "DELETED"
        room.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(room)
        return room


class RoomParticipantRepository:
    @staticmethod
    def get_by_room_and_user(
        db: Session, room_id: int, user_id: int
    ) -> Optional[RoomParticipant]:
        return (
            db.query(RoomParticipant)
            .filter(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def list_by_room(db: Session, room_id: int, state: Optional[str] = None) -> List[RoomParticipant]:
        query = db.query(RoomParticipant).filter(RoomParticipant.room_id == room_id)
        if state:
            query = query.filter(RoomParticipant.state == state)
        return query.order_by(RoomParticipant.joined_at.asc()).all()

    @staticmethod
    def count_joined(db: Session, room_id: int) -> int:
        return (
            db.query(RoomParticipant)
            .filter(
                RoomParticipant.room_id == room_id,
                RoomParticipant.state == "JOINED",
            )
            .count()
        )

    @staticmethod
    def count_ready(db: Session, room_id: int) -> int:
        return (
            db.query(RoomParticipant)
            .filter(
                RoomParticipant.room_id == room_id,
                RoomParticipant.state == "JOINED",
                RoomParticipant.is_ready.is_(True),
            )
            .count()
        )

    @staticmethod
    def create(db: Session, room_id: int, user_id: int, role: str) -> RoomParticipant:
        participant = RoomParticipant(
            room_id=room_id,
            user_id=user_id,
            role=role,
            state="JOINED",
            is_ready=False,
        )
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def update_ready(db: Session, participant: RoomParticipant, is_ready: bool) -> RoomParticipant:
        participant.is_ready = is_ready
        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def leave(db: Session, participant: RoomParticipant) -> RoomParticipant:
        from datetime import datetime
        participant.state = "LEFT"
        participant.is_ready = False
        participant.left_at = datetime.utcnow()
        db.commit()
        db.refresh(participant)
        return participant
