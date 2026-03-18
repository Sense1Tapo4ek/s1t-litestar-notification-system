from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional


def _to_utc(dt: datetime) -> datetime:
    """Ensure datetime is UTC-aware (naïve datetimes from SQLite are treated as UTC)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

from ...domain import SourceMetricsVO
from ..interfaces.i_event_log_repo import IEventLogRepo


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceSummaryDTO:
    id: str
    display_name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceStatsDTO:
    id: str
    display_name: str
    is_active: bool
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
    uptime: Optional[timedelta]
    notify_events: bool
    metrics: SourceMetricsVO


@dataclass(frozen=True, slots=True, kw_only=True)
class GetActiveSourcesListQuery:
    _repo: IEventLogRepo

    async def __call__(self) -> list[SourceSummaryDTO]:
        sources = await self._repo.get_all_active()
        return [SourceSummaryDTO(id=s.id, display_name=s.display_name) for s in sources]


@dataclass(frozen=True, slots=True, kw_only=True)
class GetInactiveSourcesListQuery:
    _repo: IEventLogRepo

    async def __call__(self) -> list[SourceSummaryDTO]:
        sources = await self._repo.get_all()
        return [
            SourceSummaryDTO(id=s.id, display_name=s.display_name)
            for s in sources if not s.is_active
        ]


@dataclass(frozen=True, slots=True, kw_only=True)
class GetSourceStatsQuery:
    _repo: IEventLogRepo

    async def __call__(self, source_id: str) -> Optional[SourceStatsDTO]:
        source = await self._repo.get_by_id(source_id)
        if not source:
            return None
        uptime = None
        if source.started_at:
            started = _to_utc(source.started_at)
            if source.is_active:
                end = datetime.now(timezone.utc)
            elif source.stopped_at:
                end = _to_utc(source.stopped_at)
            else:
                end = None
            if end:
                uptime = end - started
        return SourceStatsDTO(
            id=source.id,
            display_name=source.display_name,
            is_active=source.is_active,
            started_at=source.started_at,
            stopped_at=source.stopped_at,
            uptime=uptime,
            notify_events=source.notify_events,
            metrics=source.calculate_metrics(),
        )
