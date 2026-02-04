# Dopamine - 최저가 알리미 & 위시리스트

네이버 쇼핑 API 기반 최저가 알림 서비스

## 기술 스택

- **Backend**: FastAPI, SQLAlchemy
- **Database**: MariaDB
- **Language**: Python 3.13+

---

## 초기 세팅 가이드

### 1. 저장소 클론

```bash
git clone https://github.com/your-org/aws13th-team4-dopamine.git
cd aws13th-team4-dopamine
```

### 2. 가상환경 설정

```bash
# 가상환경 생성 (최초 1회)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 본인 환경에 맞게 수정:

```
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/dopamine
```

### 4. 서버 실행

```bash
uvicorn app.main:app --reload
```

- API 문서: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

---

## 프로젝트 구조

```
app/
├── main.py                # FastAPI 앱 진입점
├── core/                  # 핵심 설정
│   ├── config.py          # 환경변수 설정
│   ├── database.py        # DB 연결
│   └── exceptions.py      # 커스텀 예외
├── common/                # 공통 모듈
│   └── schemas.py         # 공통 스키마 (응답, 페이지네이션)
└── domain/                # 도메인별 모듈
    └── _template/         # 참고용 템플릿
        ├── models.py      # DB 모델
        ├── schemas.py     # 요청/응답 스키마
        ├── repository.py  # 데이터 접근 계층
        ├── service.py     # 비즈니스 로직
        └── router.py      # API 엔드포인트
```

### 새 도메인 생성 방법

1. `app/domain/_template` 폴더를 복사하여 새 도메인 폴더 생성
2. 각 파일의 `Template` → 실제 도메인명으로 변경
3. `app/main.py`에 라우터 등록

```python
from app.domain.user.router import router as user_router
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
```

---

## 코드 컨벤션

### Python 스타일

| 항목 | 규칙 | 예시 |
|------|------|------|
| 파일명 | snake_case | `user_service.py` |
| 클래스명 | PascalCase | `UserService` |
| 함수/변수 | snake_case | `get_user_by_id` |
| 상수 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| private | _prefix | `_validate_input` |

### 디렉토리/파일 구조

```
domain/
└── {domain_name}/
    ├── __init__.py
    ├── models.py       # SQLAlchemy 모델
    ├── schemas.py      # Pydantic 스키마
    ├── repository.py   # DB 쿼리
    ├── service.py      # 비즈니스 로직
    └── router.py       # API 라우터
```

### 네이밍 규칙

| 계층 | 클래스명 | 메서드 예시 |
|------|----------|-------------|
| Router | - | `get_users`, `create_user` |
| Service | `UserService` | `get_by_id`, `create` |
| Repository | `UserRepository` | `get_by_id`, `get_list` |
| Model | `User` | - |
| Schema | `UserCreate`, `UserResponse` | - |

### Import 순서

```python
# 1. 표준 라이브러리
from datetime import datetime
from typing import Optional, List

# 2. 서드파티 라이브러리
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. 로컬 모듈
from app.core.database import get_db
from app.domain.user.service import UserService
```

### API 응답 형식

```python
# 단건 응답
{
    "success": true,
    "message": "Success",
    "data": { ... }
}

# 목록 응답 (페이지네이션)
{
    "success": true,
    "message": "Success",
    "data": [ ... ],
    "meta": {
        "page": 1,
        "size": 20,
        "total_items": 100,
        "total_pages": 5,
        "has_next": true,
        "has_prev": false
    }
}

# 에러 응답
{
    "success": false,
    "code": "NOT_FOUND",
    "message": "User not found",
    "detail": null,
    "data": null
}
```

---

## 커밋 컨벤션

### 커밋 메시지 형식

```
<type>: <subject>
```

### Type 종류

| Type | 설명 | 예시 |
|------|------|------|
| `feat` | 새로운 기능 추가 | `feat: 회원가입 API 추가` |
| `fix` | 버그 수정 | `fix: 토큰 만료 처리 수정` |
| `refactor` | 리팩토링 | `refactor: 서비스 로직 분리` |
| `docs` | 문서 수정 | `docs: README 업데이트` |
| `style` | 코드 포맷팅 | `style: 코드 포맷 정리` |
| `test` | 테스트 코드 | `test: 회원가입 테스트 추가` |
| `chore` | 빌드, 설정 변경 | `chore: requirements.txt 업데이트` |

### 커밋 메시지 규칙

- subject는 50자 이내
- 한글 사용 가능
- 마침표 사용 X
- 명령문으로 작성 (ex: "추가", "수정", "삭제")

### 예시

```bash
# 기능 추가
git commit -m "feat: 상품 검색 API 추가"

# 버그 수정
git commit -m "fix: 위시리스트 중복 등록 버그 수정"

# 리팩토링
git commit -m "refactor: 페이지네이션 로직 개선"
```

---

## 브랜치 전략

### 브랜치 종류

| 브랜치 | 용도 | 네이밍 |
|--------|------|--------|
| `main` | 배포 브랜치 | - |
| `develop` | 개발 통합 브랜치 | - |
| `feature/*` | 기능 개발 | `feature/user-signup` |
| `fix/*` | 버그 수정 | `fix/login-error` |
| `hotfix/*` | 긴급 수정 | `hotfix/critical-bug` |

### 작업 흐름

```bash
# 1. develop에서 feature 브랜치 생성
git checkout develop
git pull origin develop
git checkout -b feature/user-signup

# 2. 작업 후 커밋
git add .
git commit -m "feat(user): 회원가입 API 추가"

# 3. 원격 저장소에 푸시
git push origin feature/user-signup

# 4. GitHub에서 PR 생성 (develop ← feature/user-signup)
```

---

## PR 규칙

1. **리뷰어 지정**: 최소 1명 이상
2. **CI 통과**: 테스트 통과 필수
3. **충돌 해결**: 머지 전 충돌 해결
4. **Squash Merge**: 커밋 정리 후 머지

---
## 브랜치 규칙
ex ) feat/이슈넘버(pr넘버)/간단한 기능설명 (두단어 이하 영어로)
feat/#1/changeLogin
---
## 팀원

| 이름 | 역할 | GitHub |
|------|------|--------|
| 박도현 | BE | - |
| 이동규 | BE | - |
| 이동준 | BE | - |
| 정민우 | BE | - |
