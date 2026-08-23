from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]

print("BASE DIR:", BASE_DIR)
print("ENV FILE:", BASE_DIR / ".env")
print("ENV EXISTS:", (BASE_DIR / ".env").exists())


class Settings(BaseSettings):

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    VERIFY_TOKEN: Optional[str] = None
    WHATSAPP_TOKEN: Optional[str] = None
    PHONE_NUMBER_ID: Optional[str] = None

    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_REDIRECT_URI: Optional[str] = None

    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None
    META_REDIRECT_URI: Optional[str] = None

    ENCRYPTION_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # JWT_SECRET_KEY: str
    # JWT_ALGORITHM: str = "HS256"
    #
    # JWT_ISSUER: str | None = None
    # JWT_AUDIENCE: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )




settings = Settings()

print("GOOGLE CLIENT ID:", settings.GOOGLE_CLIENT_ID)
print("GOOGLE SECRET:", settings.GOOGLE_CLIENT_SECRET)
print("GOOGLE REDIRECT:", settings.GOOGLE_REDIRECT_URI)
print("GOOGLE REDIRECT:", settings.DATABASE_URL)