import math
from typing import List
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.product import schemas
from app.domain.product.service import NaverShoppingService
from app.domain.product.repository import ProductRepository
from app.domain.room.service import RoomService
from app.domain.room.schemas import ProductRoomCreate, RoomResponse

# 상품 검색/상세/방 생성 API
router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
)


@router.get("/search", response_model=schemas.ProductSearchResponse)
# 네이버 쇼핑 검색 + DB 저장
def search_products(
    query: str = Query(..., description="검색 키워드", min_length=1),
    page: int = Query(1, description="페이지 번호", ge=1),
    display: int = Query(10, description="페이지 크기", ge=1, le=100),
    sort: str = Query("sim", description="정렬 (sim|date|asc|dsc)"),
    db: Session = Depends(get_db),
):
    try:
        start = ((page - 1) * display) + 1
        naver_result = NaverShoppingService.search_products(
            query=query,
            display=display,
            start=start,
            sort=sort,
        )

        parsed_products = NaverShoppingService.parse_products(naver_result)

        total_items = naver_result.get("total", 0)
        total_pages = math.ceil(total_items / display)

        return {
            "success": True,
            "message": "상품 검색 성공",
            "data": parsed_products,
            "meta": {
                "page": page,
                "size": display,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"상품 검색 실패: {str(e)}",
        )


@router.get("/{product_id}", response_model=schemas.ProductDetailResponse)
# 상품 상세 조회
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = ProductRepository.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"상품을 찾을 수 없습니다 (ID: {product_id})",
        )

    return {
        "success": True,
        "message": "상품 상세 조회 성공",
        "data": product,
    }


@router.post("/{product_id}/rooms", response_model=RoomResponse)
# 상품 기반 사다리 방 생성
def create_product_room(
    product_id: int,
    payload: ProductRoomCreate,
    x_user_id: int = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db),
):
    room_service = RoomService()
    return room_service.create_product_room(db, x_user_id, product_id, payload)


@router.get("/{product_id}/rooms", response_model=List[RoomResponse])
# 상품 기반 방 목록 조회
def list_product_rooms(
    product_id: int,
    db: Session = Depends(get_db),
):
    room_service = RoomService()
    return room_service.list_rooms_by_product(db, product_id)
