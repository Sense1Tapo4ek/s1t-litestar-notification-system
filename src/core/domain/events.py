from dataclasses import dataclass
from datetime import datetime

from .vos import EventSeverity


@dataclass(frozen=True, slots=True, kw_only=True)
class EventDetectedEvent:
    """Emitted when a new event is recorded for a source."""
    source_id: str
    source_name: str
    severity: EventSeverity
    title: str
    detail: str | None
    timestamp: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceTimeoutEvent:
    """Emitted when a source has not been seen for too long inside its active window."""
    source_id: str
    source_name: str
    last_seen: datetime
    detected_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceDiscoveredEvent:
    """Emitted the first time a source becomes active."""
    source_id: str
    source_name: str
    discovered_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceDownEvent:
    """Emitted when a previously active source goes inactive."""
    source_id: str
    source_name: str
    stopped_at: datetime
