from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file(start_path: Path) -> Path:
    for directory in [start_path, *start_path.parents]:
        env_path = directory / ".env"
        if env_path.is_file():
            return env_path
    return Path(".env")


ENV_PATH = _find_env_file(Path(__file__).resolve().parent)


class GenericConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    log_level: str = Field(default="INFO")
    volume_path: Path = Field(default=Path("./storage"))
    db_url: str = Field(default="sqlite+aiosqlite:///storage/app.sqlite")
