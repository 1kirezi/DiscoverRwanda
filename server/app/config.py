from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Discover Rwanda"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    SECRET_KEY: str = "dev-secret-key-change-in-production-must-be-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "discover_rwanda"
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/discover_rwanda"

    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 100

    REDIS_URL: str = "redis://localhost:6379/0"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM: str = "noreply@discoverrwanda.com"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
