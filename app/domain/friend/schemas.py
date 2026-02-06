from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class FriendCreate(BaseModel):
    friend_nickname: str = Field(..., min_length=2, max_length=30)


class FriendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_user_id: int
    friend_user_id: int
    created_at: datetime


class FriendListResponse(BaseModel):
    items: List[FriendResponse]
    total_count: int
    page: int
    size: int
