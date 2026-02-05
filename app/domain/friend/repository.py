from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.friend.models import Friend


class FriendRepository:
    # 친구 관계 CRUD

    @staticmethod
    # 특정 친구 관계 조회
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
    # 내 친구 목록
    def list_by_owner(db: Session, owner_user_id: int) -> List[Friend]:
        return (
            db.query(Friend)
            .filter(Friend.owner_user_id == owner_user_id)
            .order_by(Friend.created_at.desc())
            .all()
        )

    @staticmethod
    # 내 친구 총 개수
    def count_by_owner(db: Session, owner_user_id: int) -> int:
        return db.query(Friend).filter(Friend.owner_user_id == owner_user_id).count()

    @staticmethod
    # 페이지네이션 목록
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
    # 친구 추가
    def create(db: Session, owner_user_id: int, friend_user_id: int) -> Friend:
        friend = Friend(owner_user_id=owner_user_id, friend_user_id=friend_user_id)
        db.add(friend)
        db.commit()
        db.refresh(friend)
        return friend

    @staticmethod
    # 친구 삭제
    def delete(db: Session, friend: Friend) -> None:
        db.delete(friend)
        db.commit()
