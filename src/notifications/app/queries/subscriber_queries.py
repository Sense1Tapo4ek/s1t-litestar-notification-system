from dataclasses import dataclass
from typing import Optional

from notifications.app.interfaces.i_subscriber_repo import ISubscriberRepo
from notifications.domain import TelegramSubscriberEnt


@dataclass(frozen=True, slots=True, kw_only=True)
class GetSubscribersQuery:
    _repo: ISubscriberRepo

    async def __call__(self) -> list[TelegramSubscriberEnt]:
        return await self._repo.get_all()


@dataclass(frozen=True, slots=True, kw_only=True)
class GetSubscriberQuery:
    _repo: ISubscriberRepo

    async def __call__(self, chat_id: int) -> Optional[TelegramSubscriberEnt]:
        return await self._repo.get_by_chat_id(chat_id)
