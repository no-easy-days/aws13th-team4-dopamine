from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.domain.friend.models import Friend
from app.domain.friend.repository import FriendRepository
from app.domain.friend.schemas import FriendListResponse, FriendResponse
from app.domain.user.repository import UserRepository


class FriendService:
    # 친구 비즈니스 로직

    def __init__(self, repository: FriendRepository | None = None) -> None:
        self.repository = repository or FriendRepository()

    # 친구 추가 (중복/자기 자신 방지)
    def add_friend(self, db: Session, owner_user_id: int, friend_nickname: str) -> Friend:
        user_repo = UserRepository(db)
        friend_user = user_repo.get_by_nickname(friend_nickname)
        if not friend_user:
            raise NotFoundException(message="User not found")

        if owner_user_id == friend_user.id:
            raise BadRequestException(message="Cannot add yourself as a friend")

        existing = self.repository.get_by_owner_and_friend(
            db, owner_user_id=owner_user_id, friend_user_id=friend_user.id
        )
        if existing:
            raise ConflictException(message="Friend already added")

        return self.repository.create(db, owner_user_id=owner_user_id, friend_user_id=friend_user.id)

    # 친구 삭제
    def remove_friend(self, db: Session, owner_user_id: int, friend_user_id: int) -> None:
        friend = self.repository.get_by_owner_and_friend(
            db, owner_user_id=owner_user_id, friend_user_id=friend_user_id
        )
        if not friend:
            raise NotFoundException(message="Friend not found")

        self.repository.delete(db, friend)

    # 친구 목록 + total_count
    def list_friends(
        self, db: Session, owner_user_id: int, page: int, size: int
    ) -> FriendListResponse:
        total_count = self.repository.count_by_owner(db, owner_user_id=owner_user_id)
        offset = (page - 1) * size
        friends = self.repository.list_by_owner_paginated(
            db, owner_user_id=owner_user_id, offset=offset, limit=size
        )
        items = [FriendResponse.model_validate(friend) for friend in friends]
        return FriendListResponse(
            items=items, total_count=total_count, page=page, size=size
        )
