import logging
from dataclasses import dataclass
from typing import Optional

from notifications.app.interfaces.i_subscriber_repo import ISubscriberRepo
from notifications.domain import TelegramSubscriberEnt, SubscriberNotFoundError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterSubscriberUseCase:
    _repo: ISubscriberRepo

    async def __call__(self, chat_id: int, username: str) -> None:
        existing = await self._repo.get_by_chat_id(chat_id)
        if existing:
            existing.is_active = True
            await self._repo.save(existing)
            logger.info("Subscriber re-activated: %s (@%s)", chat_id, username)
        else:
            sub = TelegramSubscriberEnt(chat_id=chat_id, username=username)
            await self._repo.save(sub)
            logger.info("New subscriber registered: %s (@%s)", chat_id, username)


@dataclass(frozen=True, slots=True, kw_only=True)
class ToggleSubscriberUseCase:
    _repo: ISubscriberRepo

    async def __call__(self, chat_id: int) -> bool:
        sub = await self._repo.get_by_chat_id(chat_id)
        if not sub:
            raise SubscriberNotFoundError(chat_id=chat_id)
        sub.toggle()
        await self._repo.save(sub)
        return sub.is_active


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePreferencesCommand:
    chat_id: int
    notify_events: Optional[bool] = None
    notify_timeouts: Optional[bool] = None
    notify_services: Optional[bool] = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePreferencesUseCase:
    _repo: ISubscriberRepo

    async def __call__(self, cmd: UpdatePreferencesCommand) -> None:
        sub = await self._repo.get_by_chat_id(cmd.chat_id)
        if not sub:
            raise SubscriberNotFoundError(chat_id=cmd.chat_id)
        if cmd.notify_events is not None:
            sub.notify_events = cmd.notify_events
        if cmd.notify_timeouts is not None:
            sub.notify_timeouts = cmd.notify_timeouts
        if cmd.notify_services is not None:
            sub.notify_services = cmd.notify_services
        await self._repo.save(sub)
