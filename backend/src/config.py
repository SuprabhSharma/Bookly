from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str
    # Frontend URL for email links (verify-email, reset-password)
    FRONTEND_URL: str = "http://localhost:5173"
    # Comma-separated allowed CORS origins
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    # Comma-separated allowed hosts for TrustedHostMiddleware
    TRUSTED_HOSTS: str = "localhost,127.0.0.1"
    APP_ENV: str = "development"
    ADMIN_BOOTSTRAP_PASSWORD: str | None = None

    # Resolve the env file from the backend package, not the process cwd.
    # This keeps uvicorn, Alembic, and Docker consistent when started elsewhere.
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


Config = Settings()
