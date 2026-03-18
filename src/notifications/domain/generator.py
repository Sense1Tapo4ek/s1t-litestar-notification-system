"""
NotificationGenerator ABC -- kept in domain layer to break the circular import
between app use cases and the alerts_facade port.
"""
from abc import ABC, abstractmethod
from datetime import datetime

from core.domain import EventSeverity


class NotificationGenerator(ABC):
    """
    Transforms domain events into Telegram-ready HTML message strings.

    Subclass this to fully customise how events appear in subscriber chats.
    Register your subclass in notifications/provider.py.

    Example::

        class MyGenerator(NotificationGenerator):
            def format_event_alert(self, source_name, severity, title, detail) -> str:
                return f"[{source_name}] {title}"
            # implement other methods...
    """

    @abstractmethod
    def format_event_alert(
        self,
        source_name: str,
        severity: EventSeverity,
        title: str,
        detail: str | None,
    ) -> str:
        """Format a generic event alert."""
        ...

    @abstractmethod
    def format_timeout_alert(
        self,
        source_name: str,
        last_seen: datetime,
    ) -> str:
        """Format a source timeout (no events within active window) alert."""
        ...

    @abstractmethod
    def format_source_discovered(
        self,
        source_name: str,
        discovered_at: datetime,
    ) -> str:
        """Format a source first-seen notification."""
        ...

    @abstractmethod
    def format_source_down(
        self,
        source_name: str,
        stopped_at: datetime,
    ) -> str:
        """Format a source went-inactive notification."""
        ...
