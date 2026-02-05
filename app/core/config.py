from pydantic_settings import BaseSettings
from functools import lru_cache


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

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
