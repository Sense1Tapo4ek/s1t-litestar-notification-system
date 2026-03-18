from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.app.interfaces.i_event_log_repo import IEventLogRepo
from core.domain import EventLogAgg
from core.adapters.driven.db.orm_models import SourceModel
from .repo_mappers import source_model_to_domain, domain_to_source_model


class SqliteEventLogRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, source_id: str) -> Optional[EventLogAgg]:
        result = await self._session.get(SourceModel, source_id)
        return source_model_to_domain(result) if result else None

    async def get_all(self) -> list[EventLogAgg]:
        rows = (await self._session.scalars(select(SourceModel))).all()
        return [source_model_to_domain(r) for r in rows]

    async def get_all_active(self) -> list[EventLogAgg]:
        stmt = select(SourceModel).where(SourceModel.is_active.is_(True))
        rows = (await self._session.scalars(stmt)).all()
        return [source_model_to_domain(r) for r in rows]

    async def save(self, agg: EventLogAgg) -> None:
        existing = await self._session.get(SourceModel, agg.id)
        model = domain_to_source_model(agg, existing)
        await self._session.merge(model)
        await self._session.commit()

    async def delete(self, source_id: str) -> None:
        model = await self._session.get(SourceModel, source_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()

    async def update_last_seen(self, source_id: str, timestamp: datetime) -> None:
        stmt = (
            update(SourceModel)
            .where(SourceModel.id == source_id)
            .values(last_seen_ts=timestamp)
        )
        await self._session.execute(stmt)
        await self._session.commit()
