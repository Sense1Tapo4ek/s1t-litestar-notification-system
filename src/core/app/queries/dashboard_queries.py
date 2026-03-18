from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..interfaces.i_event_log_repo import IEventLogRepo


@dataclass(frozen=True, slots=True, kw_only=True)
class DashboardSourceDTO:
    id: str
    display_name: str
    is_active: bool
    notify_events: bool
    total_events: int
    error_count: int
    last_seen_ts: Optional[datetime]
    started_at: Optional[datetime]


@dataclass(frozen=True, slots=True, kw_only=True)
class GetDashboardQuery:
    _repo: IEventLogRepo

    async def __call__(self) -> list[DashboardSourceDTO]:
        sources = await self._repo.get_all()
        results = []
        for s in sources:
            m = s.calculate_metrics()
            results.append(DashboardSourceDTO(
                id=s.id,
                display_name=s.display_name,
                is_active=s.is_active,
                notify_events=s.notify_events,
                total_events=m.total_events,
                error_count=m.error_count + m.critical_count,
                last_seen_ts=s.last_seen_ts,
                started_at=s.started_at,
            ))
        results.sort(key=lambda s: (not s.is_active, s.display_name))
        return results
