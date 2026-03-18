"""
Anti-Corruption Layer: translates core domain events into notification commands
and calls the notifications facade. This keeps core domain independent of
the notifications context.
"""
from core.domain import (
    EventDetectedEvent, SourceTimeoutEvent, SourceDiscoveredEvent, SourceDownEvent,
)
from notifications.ports.driving.alerts_facade import (
    AlertsFacade,
    EventAlertSchema, TimeoutAlertSchema, SourceDiscoveredSchema, SourceDownSchema,
)


class NotificationACL:
    def __init__(self, alerts_facade: AlertsFacade) -> None:
        self._facade = alerts_facade

    async def send_event_detected(self, event: EventDetectedEvent) -> None:
        schema = EventAlertSchema(
            source_id=event.source_id,
            source_name=event.source_name,
            severity=event.severity,
            title=event.title,
            detail=event.detail,
            timestamp=event.timestamp,
        )
        await self._facade.notify_event_detected(schema)

    async def send_timeout_alert(self, event: SourceTimeoutEvent) -> None:
        schema = TimeoutAlertSchema(
            source_id=event.source_id,
            source_name=event.source_name,
            last_seen=event.last_seen,
            detected_at=event.detected_at,
        )
        await self._facade.notify_timeout(schema)

    async def send_source_discovered(self, event: SourceDiscoveredEvent) -> None:
        schema = SourceDiscoveredSchema(
            source_id=event.source_id,
            source_name=event.source_name,
            discovered_at=event.discovered_at,
        )
        await self._facade.notify_source_discovered(schema)

    async def send_source_down(self, event: SourceDownEvent) -> None:
        schema = SourceDownSchema(
            source_id=event.source_id,
            source_name=event.source_name,
            stopped_at=event.stopped_at,
        )
        await self._facade.notify_source_down(schema)
