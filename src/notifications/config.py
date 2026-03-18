from pydantic import Field
from pydantic_settings import SettingsConfigDict
from shared.config import GenericConfig


class NotificationsConfig(GenericConfig):
    model_config = SettingsConfigDict(
        env_prefix="NOTIFICATIONS_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_timeout_seconds: int = Field(default=10)
    telegram_api_url: str = Field(default="https://api.telegram.org")
