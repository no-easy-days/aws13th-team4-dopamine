import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.product import schemas
from app.domain.product.service import NaverShoppingService
from app.domain.product.repository import ProductRepository

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"]
)

@router.get("/search", response_model=schemas.ProductSearchResponse)
def search_products(
    query: str = Query(..., description="검색 키워드", min_length=1),
    page: int = Query(1, description="페이지 번호", ge=1),
    display: int = Query(10, description="가져올 개수", ge=1, le=100),
    sort: str = Query("sim", description="정렬 방식 (sim|date|asc|dsc)"),
    db: Session = Depends(get_db)
):
    try:

        start = ((page - 1) * display) + 1
        naver_result = NaverShoppingService.search_products(
            query=query,
            display=display,
            start=start,
            sort=sort
        )


        parsed_products = NaverShoppingService.parse_products(naver_result)
        saved_products = ProductRepository.bulk_create_or_update(db, parsed_products)


        total_items = naver_result.get("total", 0)
        total_pages = math.ceil(total_items / display)


        return {
            "success": True,
            "message": "상품 검색 성공",
            "data": saved_products,
            "meta": {
                "page": page,
                "size": display,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"상품 검색 실패: {str(e)}"
        )

@router.get("/{product_id}", response_model=schemas.ProductDetailResponse)
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = ProductRepository.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"상품을 찾을 수 없습니다 (ID: {product_id})"
        )


    return {
        "success": True,
        "message": "상품 상세 조회 성공",
        "data": product
    }