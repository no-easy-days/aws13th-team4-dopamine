from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.domain.friend.models import Friend
from app.domain.friend.repository import FriendRepository


class FriendService:
    def __init__(self, repository: FriendRepository | None = None) -> None:
        self.repository = repository or FriendRepository()

    def add_friend(self, db: Session, owner_user_id: int, friend_user_id: int) -> Friend:
        if owner_user_id == friend_user_id:
            raise BadRequestException(message="Cannot add yourself as a friend")

        existing = self.repository.get_by_owner_and_friend(
            db, owner_user_id=owner_user_id, friend_user_id=friend_user_id
        )
        if existing:
            raise ConflictException(message="Friend already added")

        return self.repository.create(db, owner_user_id=owner_user_id, friend_user_id=friend_user_id)

    def remove_friend(self, db: Session, owner_user_id: int, friend_user_id: int) -> None:
        friend = self.repository.get_by_owner_and_friend(
            db, owner_user_id=owner_user_id, friend_user_id=friend_user_id
        )
        if not friend:
            raise NotFoundException(message="Friend not found")

        self.repository.delete(db, friend)

    def list_friends(self, db: Session, owner_user_id: int) -> List[Friend]:
        return self.repository.list_by_owner(db, owner_user_id=owner_user_id)
