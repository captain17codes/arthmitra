from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ArthMitra"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/arthmitra"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/arthmitra"

    # Redis & RQ
    redis_url: str = "redis://localhost:6379/0"

    # External APIs
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    nominatim_email: str = "arthmitra@example.com"

    # Security
    secret_key: str = "insecure-default-change-in-production-1234567890"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
