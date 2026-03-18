from typing import Protocol


class ITelegramGateway(Protocol):
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool: ...
