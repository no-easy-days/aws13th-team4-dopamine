from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    status: str
    started_by_user_id: Optional[int]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    seed: Optional[str]
    created_at: datetime


class GameResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_id: int
    product_id: int
    recipient_user_id: int
    payer_user_id: int
    payment_status: str
    created_at: datetime
