from datetime import datetime
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, UniqueConstraint
from app.core.database import Base


class Friend(Base):
    __tablename__ = "friends"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    friend_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("owner_user_id", "friend_user_id", name="uq_friends_owner_friend"),
    )
