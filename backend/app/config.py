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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
