from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    """WISHLIST_GIFT 방 생성 요청"""
    wishlist_item_id: int = Field(..., gt=0, description="위시리스트 아이템 ID")
    title: Optional[str] = Field(None, max_length=120, description="방 제목")
    max_participants: int = Field(..., ge=2, le=10, description="최대 참여자 수")


class ProductRoomCreate(BaseModel):
    """PRODUCT_LADDER 방 생성 요청"""
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


class ProductInfo(BaseModel):
    """방에 연결된 상품 정보"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    image_url: Optional[str] = None
    price: Optional[int] = None
    link_url: Optional[str] = None


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
    owner_nickname: Optional[str] = None
    product_id: Optional[int]
    gift_owner_user_id: Optional[int]
    gift_owner_nickname: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    participants: List["ParticipantResponse"] = []
    current_participant_count: int = 0
    current_ready_count: int = 0
    game_result: Optional["GameResultInfo"] = None
    product: Optional[ProductInfo] = None


class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    nickname: Optional[str] = None
    role: str
    state: str
    is_ready: bool
    joined_at: datetime
    left_at: Optional[datetime] = None


class RoomListResponse(BaseModel):
    items: List[RoomResponse]


class ReadyRequest(BaseModel):
    is_ready: bool = Field(..., description="레디 상태")


class UserInfo(BaseModel):
    """유저 정보 (id + nickname)"""
    user_id: int
    nickname: str


class GameResultInfo(BaseModel):
    game_id: int
    payer_user_id: Optional[int] = None  # WISHLIST_GIFT: 참여자만 볼 수 있음
    payer_nickname: Optional[str] = None
    recipient_user_id: int
    recipient_nickname: Optional[str] = None
    product_id: int
    participant_user_ids: List[int] = []  # 방장은 참여자 목록만 볼 수 있음
    payer_user_ids: List[int] = []  # PRODUCT_LADDER: 결제자 목록 (당첨자 제외)
    payers: List[UserInfo] = []  # PRODUCT_LADDER: 결제자 정보 (id + nickname)


class ReadyResponse(BaseModel):
    participant: ParticipantResponse
    game_started: bool = False
    game_result: Optional[GameResultInfo] = None
