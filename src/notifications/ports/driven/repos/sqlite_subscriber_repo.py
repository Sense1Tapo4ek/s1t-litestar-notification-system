from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notifications.adapters.driven.db.orm_models import TelegramSubscriberModel
from notifications.domain import TelegramSubscriberEnt


def _to_domain(m: TelegramSubscriberModel) -> TelegramSubscriberEnt:
    return TelegramSubscriberEnt(
        chat_id=m.chat_id,
        username=m.username,
        is_active=m.is_active,
        notify_events=m.notify_events,
        notify_timeouts=m.notify_timeouts,
        notify_services=m.notify_services,
    )


def _to_model(e: TelegramSubscriberEnt) -> TelegramSubscriberModel:
    return TelegramSubscriberModel(
        chat_id=e.chat_id,
        username=e.username,
        is_active=e.is_active,
        notify_events=e.notify_events,
        notify_timeouts=e.notify_timeouts,
        notify_services=e.notify_services,
    )


class SqliteSubscriberRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[TelegramSubscriberEnt]:
        rows = (await self._session.scalars(select(TelegramSubscriberModel))).all()
        return [_to_domain(r) for r in rows]

    async def get_active(self) -> list[TelegramSubscriberEnt]:
        stmt = select(TelegramSubscriberModel).where(TelegramSubscriberModel.is_active.is_(True))
        return [_to_domain(r) for r in (await self._session.scalars(stmt)).all()]

    async def get_active_for_events(self) -> list[TelegramSubscriberEnt]:
        stmt = select(TelegramSubscriberModel).where(
            TelegramSubscriberModel.is_active.is_(True),
            TelegramSubscriberModel.notify_events.is_(True),
        )
        return [_to_domain(r) for r in (await self._session.scalars(stmt)).all()]

    async def get_active_for_timeouts(self) -> list[TelegramSubscriberEnt]:
        stmt = select(TelegramSubscriberModel).where(
            TelegramSubscriberModel.is_active.is_(True),
            TelegramSubscriberModel.notify_timeouts.is_(True),
        )
        return [_to_domain(r) for r in (await self._session.scalars(stmt)).all()]

    async def get_active_for_services(self) -> list[TelegramSubscriberEnt]:
        stmt = select(TelegramSubscriberModel).where(
            TelegramSubscriberModel.is_active.is_(True),
            TelegramSubscriberModel.notify_services.is_(True),
        )
        return [_to_domain(r) for r in (await self._session.scalars(stmt)).all()]

    async def get_by_chat_id(self, chat_id: int) -> Optional[TelegramSubscriberEnt]:
        model = await self._session.get(TelegramSubscriberModel, chat_id)
        return _to_domain(model) if model else None

    async def save(self, subscriber: TelegramSubscriberEnt) -> None:
        await self._session.merge(_to_model(subscriber))
        await self._session.commit()
