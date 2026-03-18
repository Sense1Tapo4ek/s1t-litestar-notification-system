from pydantic import Field
from pydantic_settings import SettingsConfigDict
from shared.config import GenericConfig


class CoreConfig(GenericConfig):
    model_config = SettingsConfigDict(
        env_prefix="CORE_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_url: str = Field(
        default="sqlite+aiosqlite:///storage/app.sqlite",
        alias="CORE_DB_URL",
        validation_alias="CORE_DB_URL",
    )
    timeout_minutes: int = Field(default=30)
