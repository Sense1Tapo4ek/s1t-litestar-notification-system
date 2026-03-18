from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .vos import EventSeverity


@dataclass(slots=True, kw_only=True)
class EventRecord:
    """
    A single detected event belonging to an EventLogAgg.
    Immutable after creation -- append-only history.
    """
    event_id: str
    severity: EventSeverity
    title: str
    timestamp: datetime
    detail: Optional[str] = None
