"""
Template Schemas - Pydantic 요청/응답 스키마 정의

사용법:
    1. 이 파일을 복사하여 실제 도메인의 schemas.py 생성
    2. 클래스명을 실제 도메인에 맞게 수정
    3. 필요한 필드 추가/수정
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# === Request Schemas ===

class TemplateCreate(BaseModel):
    """생성 요청 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="이름")
    description: Optional[str] = Field(None, description="설명")


class TemplateUpdate(BaseModel):
    """수정 요청 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="이름")
    description: Optional[str] = Field(None, description="설명")
    is_active: Optional[bool] = Field(None, description="활성화 여부")


# === Response Schemas ===

class TemplateResponse(BaseModel):
    """응답 스키마"""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TemplateListResponse(BaseModel):
    """목록 응답 스키마 (간략)"""
    id: int
    name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
