import logging
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)


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
