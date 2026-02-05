from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.product.models import Product


class ProductRepository:
    """상품 DB 작업"""

    @staticmethod
    def get_by_source_product_id(
        db: Session, source: str, source_product_id: str
    ) -> Optional[Product]:
        return (
            db.query(Product)
            .filter(
                Product.source == source,
                Product.source_product_id == source_product_id,
            )
            .first()
        )

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """상품 ID로 상세 정보 조회"""
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def count_all(db: Session) -> int:
        return db.query(Product).count()

    @staticmethod
    def list_paginated(db: Session, offset: int, limit: int) -> List[Product]:
        return (
            db.query(Product)
            .order_by(Product.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, **fields) -> Product:
        product = Product(**fields)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update(db: Session, product: Product, **fields) -> Product:
        for key, value in fields.items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete(db: Session, product: Product) -> None:
        db.delete(product)
        db.commit()
