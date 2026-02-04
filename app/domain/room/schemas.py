from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    wishlist_item_id: int = Field(..., gt=0, description="위시리스트 아이템 ID")
    title: Optional[str] = Field(None, max_length=120, description="방 제목")
    max_participants: int = Field(..., ge=2, le=10, description="최대 참여자 수")


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_type: str
    title: Optional[str]
    status: str
    max_participants: int
    is_auto_start: bool
    join_code: Optional[str]
    owner_user_id: int
    product_id: Optional[int]
    gift_owner_user_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class RoomDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_type: str
    title: Optional[str]
    status: str
    max_participants: int
    is_auto_start: bool
    join_code: Optional[str]
    owner_user_id: int
    product_id: Optional[int]
    gift_owner_user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    participants: List["ParticipantResponse"] = []
    current_ready_count: int = 0


class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    role: str
    state: str
    is_ready: bool
    joined_at: datetime
    left_at: Optional[datetime] = None


class RoomListResponse(BaseModel):
    items: List[RoomResponse]
