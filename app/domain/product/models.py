from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, UniqueConstraint, ForeignKey
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    source = Column(String(20), nullable=False)  # NAVER
    source_product_id = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    image_url = Column(Text)
    link_url = Column(Text)
    mall_name = Column(String(120))
    brand = Column(String(120))
    maker = Column(String(120))
    category1 = Column(String(120))
    category2 = Column(String(120))
    category3 = Column(String(120))
    category4 = Column(String(120))
    price = Column(Integer)
    last_fetched_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "source", "source_product_id", name="uq_products_user_source"),
    )
