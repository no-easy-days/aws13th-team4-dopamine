from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.friend.models import Friend


class FriendRepository:
    @staticmethod
    def get_by_owner_and_friend(
        db: Session, owner_user_id: int, friend_user_id: int
    ) -> Optional[Friend]:
        return (
            db.query(Friend)
            .filter(
                Friend.owner_user_id == owner_user_id,
                Friend.friend_user_id == friend_user_id,
            )
            .first()
        )

    @staticmethod
    def list_by_owner(db: Session, owner_user_id: int) -> List[Friend]:
        return (
            db.query(Friend)
            .filter(Friend.owner_user_id == owner_user_id)
            .order_by(Friend.created_at.desc())
            .all()
        )

    @staticmethod
    def count_by_owner(db: Session, owner_user_id: int) -> int:
        return db.query(Friend).filter(Friend.owner_user_id == owner_user_id).count()

    @staticmethod
    def list_by_owner_paginated(
        db: Session, owner_user_id: int, offset: int, limit: int
    ) -> List[Friend]:
        return (
            db.query(Friend)
            .filter(Friend.owner_user_id == owner_user_id)
            .order_by(Friend.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, owner_user_id: int, friend_user_id: int) -> Friend:
        friend = Friend(owner_user_id=owner_user_id, friend_user_id=friend_user_id)
        db.add(friend)
        db.commit()
        db.refresh(friend)
        return friend

    @staticmethod
    def delete(db: Session, friend: Friend) -> None:
        db.delete(friend)
        db.commit()
