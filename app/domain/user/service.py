"""
Template Service - 비즈니스 로직 계층

사용법:
    1. 이 파일을 복사하여 실제 도메인의 service.py 생성
    2. 클래스명과 의존성을 실제 도메인에 맞게 수정
    3. 비즈니스 로직 추가
"""

from typing import Tuple, List
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ConflictException
from app.domain._template.models import Template
from app.domain._template.repository import TemplateRepository
from app.domain._template.schemas import TemplateCreate, TemplateUpdate


class TemplateService:
    def __init__(self, db: Session):
        self.repository = TemplateRepository(db)

    def get_by_id(self, template_id: int) -> Template:
        """ID로 조회"""
        template = self.repository.get_by_id(template_id)
        if not template:
            raise NotFoundException(f"Template with id {template_id} not found")
        return template

    def get_list(
        self,
        page: int = 1,
        size: int = 20,
        is_active: bool | None = None,
    ) -> Tuple[List[Template], int]:
        """목록 조회"""
        offset = (page - 1) * size
        return self.repository.get_list(offset=offset, limit=size, is_active=is_active)

    def create(self, data: TemplateCreate) -> Template:
        """생성"""
        # 비즈니스 로직: 이름 중복 체크
        if self.repository.exists_by_name(data.name):
            raise ConflictException(f"Template with name '{data.name}' already exists")

        return self.repository.create(data)

    def update(self, template_id: int, data: TemplateUpdate) -> Template:
        """수정"""
        template = self.get_by_id(template_id)

        # 비즈니스 로직: 이름 변경 시 중복 체크
        if data.name and self.repository.exists_by_name(data.name, exclude_id=template_id):
            raise ConflictException(f"Template with name '{data.name}' already exists")

        return self.repository.update(template, data)

    def delete(self, template_id: int) -> None:
        """삭제"""
        template = self.get_by_id(template_id)
        self.repository.delete(template)
