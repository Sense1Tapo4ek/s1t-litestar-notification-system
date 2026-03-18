from datetime import time
from typing import Optional

from core.app import (
    GetDashboardQuery,
    GetSourceDetailsQuery,
    UpdateSourceSettingsUseCase, UpdateSourceSettingsCommand,
    ClearSourceHistoryUseCase,
    RemoveSourceUseCase,
    GetGlobalSettingsQuery, UpdateGlobalSettingsUseCase,
    GetSourceStatsQuery,
)
from .schemas import (
    SourceCardSchema, SourceDetailsSchema, EventRecordSchema,
    GlobalSettingsSchema,
)


def _fmt_time(t: Optional[time]) -> Optional[str]:
    return t.strftime("%H:%M") if t else None


def _parse_time(value: Optional[str]) -> Optional[time]:
    if not value:
        return None
    try:
        parts = value.split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


class SourceUIFacade:
    def __init__(
        self,
        dashboard_query: GetDashboardQuery,
        source_details_query: GetSourceDetailsQuery,
        source_stats_query: GetSourceStatsQuery,
        update_settings_uc: UpdateSourceSettingsUseCase,
        clear_history_uc: ClearSourceHistoryUseCase,
        remove_source_uc: RemoveSourceUseCase,
        global_settings_query: GetGlobalSettingsQuery,
        update_global_settings_uc: UpdateGlobalSettingsUseCase,
    ) -> None:
        self._dashboard_query = dashboard_query
        self._source_details_query = source_details_query
        self._source_stats_query = source_stats_query
        self._update_settings_uc = update_settings_uc
        self._clear_history_uc = clear_history_uc
        self._remove_source_uc = remove_source_uc
        self._global_settings_query = global_settings_query
        self._update_global_settings_uc = update_global_settings_uc

    async def get_dashboard(self) -> list[SourceCardSchema]:
        items = await self._dashboard_query()
        return [
            SourceCardSchema(
                id=item.id,
                display_name=item.display_name,
                is_active=item.is_active,
                notify_events=item.notify_events,
                total_events=item.total_events,
                error_count=item.error_count,
                last_seen_ts=item.last_seen_ts,
                started_at=item.started_at,
            )
            for item in items
        ]

    async def get_source_details(self, source_id: str) -> Optional[SourceDetailsSchema]:
        agg = await self._source_details_query(source_id)
        if not agg:
            return None
        stats = await self._source_stats_query(source_id)
        m = agg.calculate_metrics()

        recent = sorted(agg.events, key=lambda e: e.timestamp, reverse=True)[:50]

        return SourceDetailsSchema(
            id=agg.id,
            display_name=agg.display_name,
            custom_name=agg.custom_name,
            is_active=agg.is_active,
            notify_events=agg.notify_events,
            started_at=agg.started_at,
            stopped_at=agg.stopped_at,
            uptime_seconds=int(stats.uptime.total_seconds()) if stats and stats.uptime else None,
            total_events=m.total_events,
            info_count=m.info_count,
            warning_count=m.warning_count,
            error_count=m.error_count,
            critical_count=m.critical_count,
            error_rate=float(m.error_rate),
            active_window_start=_fmt_time(agg.active_window.start_time) if agg.active_window else None,
            active_window_end=_fmt_time(agg.active_window.end_time) if agg.active_window else None,
            recent_events=[
                EventRecordSchema(
                    event_id=e.event_id,
                    severity=e.severity,
                    title=e.title,
                    detail=e.detail,
                    timestamp=e.timestamp,
                )
                for e in recent
            ],
        )

    async def update_settings(
        self,
        source_id: str,
        custom_name: Optional[str],
        notify_events: bool,
        active_window_start: Optional[str],
        active_window_end: Optional[str],
    ) -> None:
        cmd = UpdateSourceSettingsCommand(
            source_id=source_id,
            custom_name=custom_name,
            notify_events=notify_events,
            active_window_start=_parse_time(active_window_start),
            active_window_end=_parse_time(active_window_end),
        )
        await self._update_settings_uc(cmd)

    async def clear_history(self, source_id: str) -> None:
        await self._clear_history_uc(source_id)

    async def remove_source(self, source_id: str) -> None:
        await self._remove_source_uc(source_id)

    async def get_global_settings(self) -> GlobalSettingsSchema:
        start, end = await self._global_settings_query()
        return GlobalSettingsSchema(
            active_window_start=_fmt_time(start),
            active_window_end=_fmt_time(end),
        )

    async def update_global_settings(
        self, active_window_start: Optional[str], active_window_end: Optional[str]
    ) -> None:
        await self._update_global_settings_uc(
            start=_parse_time(active_window_start),
            end=_parse_time(active_window_end),
        )
