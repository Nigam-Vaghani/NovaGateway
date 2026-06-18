from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/novagateway"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "supersecret_change_in_production"
    ALLOWED_HOSTS: str = "*"
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    HEALTH_CHECK_INTERVAL: int = 30
    LOG_LEVEL: str = "INFO"
    PROXY_TARGET_URL: str = "http://localhost:8001"

    MAX_REQUEST_SIZE_MB: int = 10
    MAX_RETRIES: int = 3
    LOAD_BALANCER_STRATEGY: str = "round_robin"

    SSL_CERTFILE: Optional[str] = None
    SSL_KEYFILE: Optional[str] = None
    HTTP_REDIRECT_PORT: int = 80
    HTTPS_PORT: int = 443

    @property
    def is_https_active(self) -> bool:
        return bool(self.SSL_CERTFILE and self.SSL_KEYFILE)

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
