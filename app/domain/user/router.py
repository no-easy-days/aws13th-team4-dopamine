"""
Template Router - API 엔드포인트 정의

사용법:
    1. 이 파일을 복사하여 실제 도메인의 router.py 생성
    2. 경로와 태그를 실제 도메인에 맞게 수정
    3. main.py에 라우터 등록:
       from app.domain.{domain}.router import router as {domain}_router
       app.include_router({domain}_router, prefix="/api/v1/{domain}s", tags=["{domain}s"])
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.common.schemas import BaseResponse, PagedResponse, PageMeta, PageParams
from app.domain._template.service import TemplateService
from app.domain._template.schemas import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
)

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> TemplateService:
    return TemplateService(db)


@router.get("", response_model=PagedResponse[TemplateListResponse])
async def get_templates(
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=20, ge=1, le=100, description="페이지 크기"),
    is_active: Optional[bool] = Query(default=None, description="활성화 여부 필터"),
    service: TemplateService = Depends(get_service),
):
    """템플릿 목록 조회"""
    items, total = service.get_list(page=page, size=size, is_active=is_active)
    return PagedResponse(
        data=[TemplateListResponse.model_validate(item) for item in items],
        meta=PageMeta.create(page=page, size=size, total_items=total),
    )


@router.get("/{template_id}", response_model=BaseResponse[TemplateResponse])
async def get_template(
    template_id: int,
    service: TemplateService = Depends(get_service),
):
    """템플릿 단건 조회"""
    template = service.get_by_id(template_id)
    return BaseResponse.ok(data=TemplateResponse.model_validate(template))


@router.post("", response_model=BaseResponse[TemplateResponse], status_code=201)
async def create_template(
    data: TemplateCreate,
    service: TemplateService = Depends(get_service),
):
    """템플릿 생성"""
    template = service.create(data)
    return BaseResponse.ok(data=TemplateResponse.model_validate(template), message="Created")


@router.put("/{template_id}", response_model=BaseResponse[TemplateResponse])
async def update_template(
    template_id: int,
    data: TemplateUpdate,
    service: TemplateService = Depends(get_service),
):
    """템플릿 수정"""
    template = service.update(template_id, data)
    return BaseResponse.ok(data=TemplateResponse.model_validate(template), message="Updated")


@router.delete("/{template_id}", response_model=BaseResponse)
async def delete_template(
    template_id: int,
    service: TemplateService = Depends(get_service),
):
    """템플릿 삭제"""
    service.delete(template_id)
    return BaseResponse.ok(message="Deleted")
