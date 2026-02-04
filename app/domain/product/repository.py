from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.product.models import Product


class ProductRepository:
    """상품 DB 작업"""
    @staticmethod
    def bulk_create_or_update(db: Session, products_data: List[dict]) -> List[Product]:
        saved_products = []

        for product_data in products_data:
            # 중복 체크
            existing = db.query(Product).filter(
                Product.source == product_data["source"],
                Product.source_product_id == product_data["source_product_id"]
            ).first()

            if existing:
                # 업데이트
                for key, value in product_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                saved_products.append(existing)
            else:
                # 새 저장
                new_product = Product(**product_data)
                db.add(new_product)
                saved_products.append(new_product)


        db.commit()


        for p in saved_products:
            db.refresh(p)

        return saved_products

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        상품 ID로 상세 정보를 조회합니다.
        """
        return db.query(Product).filter(Product.id == product_id).first()