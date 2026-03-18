from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...domain import EventLogAgg, EventSeverity
from ..interfaces.i_event_log_repo import IEventLogRepo
from ..interfaces.i_notification_gateway import INotificationGateway
from ..errors import SourceNotFoundError


@dataclass(frozen=True, slots=True, kw_only=True)
class ProcessEventCommand:
    """
    Sent by NotificationDetector to record an event from an external source.
    This is the primary ingestion command of the system.
    """
    source_id: str
    event_id: str
    severity: EventSeverity
    title: str
    timestamp: datetime
    detail: Optional[str] = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ProcessEventUseCase:
    """
    Records a new event and dispatches notification if source has notify_events=True.

    The source must already exist (auto-registered by DetectorManager or manually via
    ManageSourceUseCase). Raises SourceNotFoundError otherwise.
    """
    _repo: IEventLogRepo
    _notifier: INotificationGateway

    async def __call__(self, cmd: ProcessEventCommand) -> None:
        agg = await self._repo.get_by_id(cmd.source_id)
        if not agg:
            raise SourceNotFoundError(source_id=cmd.source_id)

        domain_event = agg.record_event(
            event_id=cmd.event_id,
            severity=cmd.severity,
            title=cmd.title,
            timestamp=cmd.timestamp,
            detail=cmd.detail,
        )
        await self._repo.save(agg)

        if domain_event is not None:
            await self._notifier.send_event_detected(domain_event)
