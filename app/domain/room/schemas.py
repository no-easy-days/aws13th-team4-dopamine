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
    current_participant_count: int = 0


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
    current_participant_count: int = 0
    current_ready_count: int = 0
    game_result: Optional["GameResultInfo"] = None


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


class ReadyRequest(BaseModel):
    is_ready: bool = Field(..., description="레디 상태")


class GameResultInfo(BaseModel):
    game_id: int
    payer_user_id: Optional[int] = None  # 참여자만 볼 수 있음
    recipient_user_id: int
    product_id: int
    participant_user_ids: List[int] = []  # 방장은 참여자 목록만 볼 수 있음


class ReadyResponse(BaseModel):
    participant: ParticipantResponse
    game_started: bool = False
    game_result: Optional[GameResultInfo] = None
