from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    room_type = Column(String(30), nullable=False, index=True)  # PRODUCT_LADDER | WISHLIST_GIFT
    title = Column(String(120))
    status = Column(String(20), nullable=False, index=True)  # OPEN | RUNNING | DONE | CLOSED | DELETED
    max_participants = Column(Integer, nullable=False)
    is_auto_start = Column(Boolean, nullable=False, default=True)
    join_code = Column(String(32), unique=True)
    owner_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), index=True)  # PRODUCT_LADDER 필수
    gift_owner_user_id = Column(BigInteger, ForeignKey("users.id"), index=True)  # WISHLIST_GIFT 필수
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)


class RoomParticipant(Base):
    __tablename__ = "room_participants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("rooms.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # OWNER | MEMBER
    state = Column(String(20), nullable=False)  # JOINED | LEFT
    is_ready = Column(Boolean, nullable=False, default=False, index=True)
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    left_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="uq_room_participants"),
    )


class RoomItem(Base):
    __tablename__ = "room_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("rooms.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("room_id", "product_id", name="uq_room_items"),
    )
