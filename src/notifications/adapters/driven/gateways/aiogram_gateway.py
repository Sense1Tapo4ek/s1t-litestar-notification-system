import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from notifications.app.interfaces.i_telegram_gateway import ITelegramGateway

logger = logging.getLogger(__name__)


class TelegramGatewayRef:
    """Mutable holder for the gateway — updated by telegram_supervisor at runtime."""

    def __init__(self) -> None:
        self._gateway: Optional[ITelegramGateway] = None

    def set(self, gateway: Optional[ITelegramGateway]) -> None:
        self._gateway = gateway

    def get(self) -> Optional[ITelegramGateway]:
        return self._gateway


class AiogramGateway:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        try:
            await self._bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            return True
        except TelegramAPIError as exc:
            logger.warning("Telegram API error sending to %s: %s", chat_id, exc)
            return False
        except Exception:
            logger.exception("Unexpected error sending to %s", chat_id)
            return False
