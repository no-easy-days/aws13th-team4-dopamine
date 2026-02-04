"""
Template Model - SQLAlchemy 모델 정의

사용법:
    1. 이 파일을 복사하여 실제 도메인의 models.py 생성
    2. 클래스명과 테이블명을 실제 도메인에 맞게 수정
    3. 필요한 컬럼 추가/수정
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.core.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name})>"
