from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class FriendCreate(BaseModel):
    friend_user_id: int = Field(..., gt=0)


class FriendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_user_id: int
    friend_user_id: int
    created_at: datetime


class FriendListResponse(BaseModel):
    items: List[FriendResponse]
