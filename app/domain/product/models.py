from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, UniqueConstraint
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    # 외부 쇼핑 API 결과를 저장하는 캐시 테이블
    id = Column(BigInteger, primary_key=True, autoincrement=True)
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

    # source + source_product_id 조합으로 유니크 보장
    __table_args__ = (
        UniqueConstraint("source", "source_product_id", name="uq_products_source"),
    )
