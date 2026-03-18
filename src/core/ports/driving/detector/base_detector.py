"""
NotificationDetector -- abstract base for all event source detectors.

Subclass this to integrate a real external source (a log file, a Kafka topic,
a REST health-check endpoint, etc.).  The system calls `run()` in a background
task; you call `on_event()` whenever something happens.

Example::

    class MyDetector(NotificationDetector):
        async def run(self, on_event):
            async for line in tail_my_log():
                if "ERROR" in line:
                    await on_event(
                        source_id="my-service",
                        event_id=str(uuid4()),
                        severity=EventSeverity.ERROR,
                        title=line[:120],
                        detail=line,
                    )
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Awaitable, Callable

from core.domain import EventSeverity

OnEventCallback = Callable[
    [str, str, EventSeverity, str, str | None, datetime | None],
    Awaitable[None],
]
"""
Args: source_id, event_id, severity, title, detail, timestamp
"""


class NotificationDetector(ABC):
    """
    Abstract event detector.

    The worker calls ``run(on_event)`` once and keeps the task alive.
    Call ``on_event(source_id, event_id, severity, title, detail, timestamp)``
    each time you detect something worth recording.
    """

    @abstractmethod
    async def run(self, on_event: OnEventCallback) -> None:
        """
        Long-running detection loop.  Must not return until stopped.
        Implement your polling / subscription / file-tailing logic here.
        """
        ...

    async def stop(self) -> None:
        """
        Called during graceful shutdown.  Override to cancel subscriptions,
        close connections, etc.
        """
        ...
