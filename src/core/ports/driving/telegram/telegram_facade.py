from typing import Optional

from core.app import (
    GetDashboardQuery,
    GetSourceStatsQuery,
)
from .schemas import TgSourceCardSchema, TgSourceStatsSchema


class CoreTelegramFacade:
    """
    Facade used by the Telegram handler (notifications context) to query
    information about event sources without crossing context boundaries
    via direct imports.
    """
    def __init__(
        self,
        dashboard_query: GetDashboardQuery,
        source_stats_query: GetSourceStatsQuery,
    ) -> None:
        self._dashboard_query = dashboard_query
        self._source_stats_query = source_stats_query

    async def list_sources(self) -> list[TgSourceCardSchema]:
        items = await self._dashboard_query()
        return [
            TgSourceCardSchema(
                id=item.id,
                display_name=item.display_name,
                is_active=item.is_active,
                total_events=item.total_events,
                error_count=item.error_count,
                last_seen_ts=item.last_seen_ts,
            )
            for item in items
        ]

    async def get_source_stats(self, source_id: str) -> Optional[TgSourceStatsSchema]:
        dto = await self._source_stats_query(source_id)
        if not dto:
            return None
        return TgSourceStatsSchema(
            id=dto.id,
            display_name=dto.display_name,
            is_active=dto.is_active,
            total_events=dto.metrics.total_events,
            info_count=dto.metrics.info_count,
            warning_count=dto.metrics.warning_count,
            error_count=dto.metrics.error_count,
            critical_count=dto.metrics.critical_count,
            started_at=dto.started_at,
            stopped_at=dto.stopped_at,
            uptime_seconds=int(dto.uptime.total_seconds()) if dto.uptime else None,
        )
