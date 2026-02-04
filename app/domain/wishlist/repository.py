from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.domain.product.models import Product
from app.domain.product.models import Product
from app.domain.wishlist.models import WishlistItem


class WishlistRepository:
    @staticmethod
    def get_by_user_and_product(
        db: Session, user_id: int, product_id: int
    ) -> Optional[WishlistItem]:
        return (
            db.query(WishlistItem)
            .filter(WishlistItem.user_id == user_id, WishlistItem.product_id == product_id)
            .first()
        )

    @staticmethod
    def list_items_with_product(
        db: Session, user_id: int
    ) -> List[Tuple[WishlistItem, Product]]:
        return (
            db.query(WishlistItem, Product)
            .join(Product, WishlistItem.product_id == Product.id)
            .filter(WishlistItem.user_id == user_id)
            .order_by(WishlistItem.created_at.desc())
            .all()
        )

    @staticmethod
    def create(
        db: Session, user_id: int, product_id: int, memo: str | None, priority: int | None
    ) -> WishlistItem:
        item = WishlistItem(
            user_id=user_id, product_id=product_id, memo=memo, priority=priority
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item: WishlistItem) -> None:
        db.delete(item)
        db.commit()
