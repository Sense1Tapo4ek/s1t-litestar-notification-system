from typing import Protocol, Optional
from notifications.domain import TelegramConfigAgg


class IConfigRepo(Protocol):
    async def get(self) -> TelegramConfigAgg: ...
    async def save(self, agg: TelegramConfigAgg) -> None: ...
