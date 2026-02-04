from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey, UniqueConstraint
from app.core.database import Base


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False, index=True)
    memo = Column(String(255))
    priority = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )
