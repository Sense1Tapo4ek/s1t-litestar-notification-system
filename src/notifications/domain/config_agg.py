from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, kw_only=True)
class TelegramConfigAgg:
    """Aggregate holding the Telegram Bot token."""
    _SINGLETON_ID = "telegram"
    id: str = _SINGLETON_ID
    bot_token: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token)

    def set_token(self, token: str) -> None:
        self.bot_token = token.strip()
