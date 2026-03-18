from dataclasses import dataclass
from datetime import datetime, timezone, time
from typing import Optional

from ...domain import EventLogAgg, TimeWindowVO
from ..interfaces.i_event_log_repo import IEventLogRepo
from ..errors import SourceNotFoundError


@dataclass(frozen=True, slots=True, kw_only=True)
class AddSourceUseCase:
    """Register a new event source. Idempotent -- returns silently if already exists."""
    _repo: IEventLogRepo

    async def __call__(self, source_id: str, display_name: Optional[str] = None) -> None:
        existing = await self._repo.get_by_id(source_id)
        if existing:
            return
        agg = EventLogAgg(
            id=source_id,
            custom_name=display_name,
            is_active=True,
            started_at=datetime.now(timezone.utc),
        )
        await self._repo.save(agg)


@dataclass(frozen=True, slots=True, kw_only=True)
class RemoveSourceUseCase:
    """Remove a source and all its event history."""
    _repo: IEventLogRepo

    async def __call__(self, source_id: str) -> None:
        await self._repo.delete(source_id)


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateSourceSettingsCommand:
    source_id: str
    custom_name: Optional[str] = None
    notify_events: Optional[bool] = None
    active_window_start: Optional[time] = None
    active_window_end: Optional[time] = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateSourceSettingsUseCase:
    _repo: IEventLogRepo

    async def __call__(self, cmd: UpdateSourceSettingsCommand) -> None:
        agg = await self._repo.get_by_id(cmd.source_id)
        if not agg:
            raise SourceNotFoundError(source_id=cmd.source_id)
        if cmd.custom_name is not None:
            agg.set_custom_name(cmd.custom_name)
        if cmd.notify_events is not None:
            agg.set_notify_events(cmd.notify_events)
        if cmd.active_window_start is not None and cmd.active_window_end is not None:
            agg.set_active_window(TimeWindowVO(
                start_time=cmd.active_window_start,
                end_time=cmd.active_window_end,
            ))
        elif cmd.active_window_start is None and cmd.active_window_end is None:
            pass
        else:
            agg.set_active_window(None)
        await self._repo.save(agg)


@dataclass(frozen=True, slots=True, kw_only=True)
class ClearSourceHistoryUseCase:
    _repo: IEventLogRepo

    async def __call__(self, source_id: str) -> None:
        agg = await self._repo.get_by_id(source_id)
        if not agg:
            raise SourceNotFoundError(source_id=source_id)
        agg.clear_history()
        await self._repo.save(agg)


@dataclass(frozen=True, slots=True, kw_only=True)
class MarkSourceActiveUseCase:
    """Used by DetectorManager to transition a source to active state."""
    _repo: IEventLogRepo
    _notifier: "INotificationGateway"

    async def __call__(self, source_id: str, started_at: datetime) -> None:
        from ..interfaces.i_notification_gateway import INotificationGateway
        agg = await self._repo.get_by_id(source_id)
        if not agg:
            agg = EventLogAgg(id=source_id, is_active=False)
        event = agg.mark_active(started_at)
        await self._repo.save(agg)
        if event:
            await self._notifier.send_source_discovered(event)


@dataclass(frozen=True, slots=True, kw_only=True)
class MarkSourceInactiveUseCase:
    """Used by DetectorManager to transition a source to inactive."""
    _repo: IEventLogRepo
    _notifier: "INotificationGateway"

    async def __call__(self, source_id: str, stopped_at: datetime) -> None:
        agg = await self._repo.get_by_id(source_id)
        if not agg:
            return
        event = agg.mark_inactive(stopped_at)
        await self._repo.save(agg)
        if event:
            await self._notifier.send_source_down(event)
