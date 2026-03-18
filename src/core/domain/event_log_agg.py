from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from .ents import EventRecord
from .vos import EventSeverity, TimeWindowVO, SourceMetricsVO
from .events import EventDetectedEvent, SourceTimeoutEvent, SourceDiscoveredEvent, SourceDownEvent
from .errors import DuplicateEventError


@dataclass(slots=True, kw_only=True)
class EventLogAgg:
    """
    Aggregate Root for an event source.

    An event source is any external system, service, or process that produces
    structured events (e.g. a microservice, a batch job, a sensor feed).
    The aggregate maintains the full event history and lifecycle state.

    Primary key: id (set by the user -- any unique string).
    """
    id: str
    custom_name: Optional[str] = None
    notify_events: bool = True
    active_window: Optional[TimeWindowVO] = None

    is_active: bool = False
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    last_seen_ts: Optional[datetime] = None

    events: list[EventRecord] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def display_name(self) -> str:
        return self.custom_name if self.custom_name else self.id

    # ------------------------------------------------------------------
    # Domain methods
    # ------------------------------------------------------------------

    def record_event(
        self,
        event_id: str,
        severity: EventSeverity,
        title: str,
        timestamp: datetime,
        detail: Optional[str] = None,
    ) -> Optional[EventDetectedEvent]:
        """
        Append a new event to the history.
        Returns a domain event for notification dispatch if notify_events is True.
        Raises DuplicateEventError on repeated event_id.
        """
        for e in self.events:
            if e.event_id == event_id:
                raise DuplicateEventError(source_id=self.id, event_id=event_id)

        record = EventRecord(
            event_id=event_id,
            severity=severity,
            title=title,
            timestamp=timestamp,
            detail=detail,
        )
        self.events.append(record)
        self.last_seen_ts = timestamp

        if not self.notify_events:
            return None

        return EventDetectedEvent(
            source_id=self.id,
            source_name=self.display_name,
            severity=severity,
            title=title,
            detail=detail,
            timestamp=timestamp,
        )

    def mark_active(self, started_at: datetime) -> Optional[SourceDiscoveredEvent]:
        """Transition to active. Returns a discovered event on first activation."""
        if self.is_active:
            return None
        self.is_active = True
        self.started_at = started_at
        self.stopped_at = None
        return SourceDiscoveredEvent(
            source_id=self.id,
            source_name=self.display_name,
            discovered_at=started_at,
        )

    def mark_inactive(self, stopped_at: datetime) -> Optional[SourceDownEvent]:
        """Transition to inactive."""
        if not self.is_active:
            return None
        self.is_active = False
        self.stopped_at = stopped_at
        return SourceDownEvent(
            source_id=self.id,
            source_name=self.display_name,
            stopped_at=stopped_at,
        )

    def check_timeout(
        self,
        current_ts: datetime,
        timeout_minutes: int = 30,
    ) -> Optional[SourceTimeoutEvent]:
        """
        Check if the source has been silent too long.
        Only fires within the configured active_window (if set).
        """
        if not self.is_active:
            return None
        if not self.last_seen_ts or not self.active_window:
            return None
        if not self.active_window.is_active_at(current_ts.time()):
            return None
        if current_ts - self.last_seen_ts > timedelta(minutes=timeout_minutes):
            return SourceTimeoutEvent(
                source_id=self.id,
                source_name=self.display_name,
                last_seen=self.last_seen_ts,
                detected_at=current_ts,
            )
        return None

    def calculate_metrics(self) -> SourceMetricsVO:
        counts = {s: 0 for s in EventSeverity}
        for e in self.events:
            counts[e.severity] += 1
        return SourceMetricsVO(
            total_events=len(self.events),
            info_count=counts[EventSeverity.INFO],
            warning_count=counts[EventSeverity.WARNING],
            error_count=counts[EventSeverity.ERROR],
            critical_count=counts[EventSeverity.CRITICAL],
        )

    def clear_history(self) -> None:
        self.events.clear()

    def set_custom_name(self, name: Optional[str]) -> None:
        self.custom_name = name

    def set_notify_events(self, value: bool) -> None:
        self.notify_events = value

    def set_active_window(self, window: Optional[TimeWindowVO]) -> None:
        self.active_window = window
