"""
Application configuration. Loads and validates all environment
variables in one place using pydantic-settings — every other module
imports `settings` from here instead of calling os.getenv() directly.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Telegram ---
    BOT_TOKEN: str
    WEBHOOK_URL: str
    WEBHOOK_SECRET: str

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./tts_bot.db"

    # --- TTS engine ---
    TTS_ENGINE: str = "gtts"  # "gtts" or "openai"
    OPENAI_API_KEY: str | None = None
    OPENAI_TTS_MODEL: str = "tts-1"

    # --- Limits ---
    MAX_TEXT_LENGTH: int = 4000

    # --- Logging / environment ---
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def webhook_path(self) -> str:
        return f"/webhook/{self.WEBHOOK_SECRET}"

    @property
    def full_webhook_url(self) -> str:
        return f"{self.WEBHOOK_URL.rstrip('/')}{self.webhook_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
