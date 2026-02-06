from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/dopamine"

    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_TITLE: str = "니가내 API"
    APP_VERSION: str = "1.0.0"
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""

<<<<<<< HEAD
    # JWT
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 14
=======
    # JWT 설정 (실제 값은 .env에서 설정)
    JWT_SECRET_KEY: str = ""  # 필수: .env에서 설정
    JWT_EXPIRE_HOURS: int = 24
>>>>>>> origin/main

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
