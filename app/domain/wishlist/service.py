from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.domain.friend.repository import FriendRepository
from app.domain.product.models import Product
from app.domain.wishlist.repository import WishlistRepository
from app.domain.wishlist.schemas import (
    WishlistCreate,
    WishlistItemResponse,
    WishlistProductResponse,
)


class WishlistService:
    def __init__(
        self,
        wishlist_repository: WishlistRepository | None = None,
        friend_repository: FriendRepository | None = None,
    ) -> None:
        self.wishlist_repository = wishlist_repository or WishlistRepository()
        self.friend_repository = friend_repository or FriendRepository()

    def list_friend_wishlist(
        self, db: Session, requester_id: int, friend_user_id: int
    ) -> List[WishlistItemResponse]:
        relation = self.friend_repository.get_by_owner_and_friend(
            db, owner_user_id=requester_id, friend_user_id=friend_user_id
        )
        if not relation:
            raise ForbiddenException(message="Not a friend")

        rows = self.wishlist_repository.list_items_with_product(
            db, user_id=friend_user_id
        )

        items: List[WishlistItemResponse] = []
        for wishlist_item, product in rows:
            item = WishlistItemResponse.model_validate(wishlist_item)
            item.product = WishlistProductResponse.model_validate(product)
            items.append(item)
        return items

    def list_my_wishlist(self, db: Session, user_id: int) -> List[WishlistItemResponse]:
        rows = self.wishlist_repository.list_items_with_product(db, user_id=user_id)
        items: List[WishlistItemResponse] = []
        for wishlist_item, product in rows:
            item = WishlistItemResponse.model_validate(wishlist_item)
            item.product = WishlistProductResponse.model_validate(product)
            items.append(item)
        return items

    def add_to_wishlist(
        self, db: Session, user_id: int, payload: WishlistCreate
    ) -> WishlistItemResponse:
        product = (
            db.query(Product)
            .filter(Product.id == payload.product_id, Product.user_id == user_id)
            .first()
        )
        if not product:
            raise NotFoundException(message="Product not found")

        existing = self.wishlist_repository.get_by_user_and_product(
            db, user_id=user_id, product_id=payload.product_id
        )
        if existing:
            raise ConflictException(message="Product already in wishlist")

        item = self.wishlist_repository.create(
            db,
            user_id=user_id,
            product_id=payload.product_id,
            memo=payload.memo,
            priority=payload.priority,
        )
        response = WishlistItemResponse.model_validate(item)
        response.product = WishlistProductResponse.model_validate(product)
        return response

    def remove_from_wishlist(self, db: Session, user_id: int, product_id: int) -> None:
        item = self.wishlist_repository.get_by_user_and_product(
            db, user_id=user_id, product_id=product_id
        )
        if not item:
            raise NotFoundException(message="Wishlist item not found")

        self.wishlist_repository.delete(db, item)
