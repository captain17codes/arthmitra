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
    sarvam_api_key: str = ""
    sarvam_asr_url: str = "https://api.sarvam.ai/speech-to-text"
    bhashini_api_key: str = ""
    bhashini_user_id: str = ""
    bhashini_pipeline_id: str = ""
    asr_provider: str = "auto"  # "auto", "sarvam", "bhashini", "mock"

    # Security
    secret_key: str = "insecure-default-change-in-production-1234567890"
    # Optional dedicated key for PII encryption. If unset, it is derived from secret_key
    # (kept for backward compatibility with data already encrypted that way).
    encryption_key: str = ""
    # Comma-separated browser origins allowed to call the API directly (Vercel proxies same-origin).
    cors_origins: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    notice_version_current: str = "v1.0-2026-04"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


INSECURE_DEFAULT_SECRET = "insecure-default-change-in-production-1234567890"

settings = Settings()
