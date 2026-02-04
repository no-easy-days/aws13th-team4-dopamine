"""
=== TEMPLATE DOMAIN ===

이 폴더는 새로운 도메인 생성 시 참고용 템플릿입니다.
실제 도메인을 만들 때 이 폴더를 복사하여 사용하세요.

예시: user 도메인 생성 시
    1. _template 폴더를 복사하여 user 폴더 생성
    2. 각 파일의 Template -> User 로 변경
    3. main.py에 라우터 등록

구조 설명:
    - models.py: SQLAlchemy 모델 (DB 테이블)
    - schemas.py: Pydantic 스키마 (요청/응답)
    - repository.py: 데이터 접근 계층 (CRUD)
    - service.py: 비즈니스 로직 계층
    - router.py: API 엔드포인트 정의
"""
