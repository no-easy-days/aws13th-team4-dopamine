from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.product.models import Product


class ProductRepository:
    """상품 DB 작업"""


    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """상품 ID로 상세 정보 조회"""
        return db.query(Product).filter(Product.id == product_id).first()
