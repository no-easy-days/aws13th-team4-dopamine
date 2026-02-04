from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from app.core.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("rooms.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)  # READY | RUNNING | DONE | CANCELED
    started_by_user_id = Column(BigInteger, ForeignKey("users.id"))
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    seed = Column(String(64))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    game_id = Column(BigInteger, ForeignKey("games.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False, index=True)
    recipient_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    payer_user_id = Column(BigInteger, ForeignKey("users.id"), index=True)  # WISHLIST_GIFT용 (단일 결제자)
    payment_status = Column(String(20), nullable=False, default="PENDING")  # PENDING | PAID | FAILED | CANCELED
    fake_payment_id = Column(String(64))
    paid_at = Column(DateTime)
    message_sent_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class GamePayer(Base):
    """PRODUCT_LADDER 방용 - 다중 결제자"""
    __tablename__ = "game_payers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    game_result_id = Column(BigInteger, ForeignKey("game_results.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    payment_status = Column(String(20), nullable=False, default="PENDING")  # PENDING | PAID | FAILED
    paid_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
