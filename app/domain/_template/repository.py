"""
Template Repository - 데이터 접근 계층

사용법:
    1. 이 파일을 복사하여 실제 도메인의 repository.py 생성
    2. 클래스명과 모델을 실제 도메인에 맞게 수정
    3. 필요한 쿼리 메서드 추가
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain._template.models import Template
from app.domain._template.schemas import TemplateCreate, TemplateUpdate


class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, template_id: int) -> Optional[Template]:
        """ID로 단건 조회"""
        return self.db.get(Template, template_id)

    def get_list(
        self,
        offset: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Template], int]:
        """목록 조회 (페이지네이션)"""
        query = select(Template)

        # 필터 조건
        if is_active is not None:
            query = query.where(Template.is_active == is_active)

        # 총 개수
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.scalar(count_query) or 0

        # 페이지네이션 적용
        query = query.order_by(Template.id.desc()).offset(offset).limit(limit)
        items = list(self.db.scalars(query).all())

        return items, total

    def create(self, data: TemplateCreate) -> Template:
        """생성"""
        template = Template(**data.model_dump())
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template: Template, data: TemplateUpdate) -> Template:
        """수정"""
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(template, key, value)
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template: Template) -> None:
        """삭제"""
        self.db.delete(template)
        self.db.commit()

    def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """이름 중복 체크"""
        query = select(Template.id).where(Template.name == name)
        if exclude_id:
            query = query.where(Template.id != exclude_id)
        return self.db.scalar(query) is not None
