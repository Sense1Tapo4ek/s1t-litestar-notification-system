"""
AlertsFacade -- driving port for the core context ACL to dispatch notifications.

Also defines DefaultGenerator -- the built-in NotificationGenerator implementation.
NotificationGenerator ABC lives in notifications/domain/generator.py to avoid circular imports.
"""
from dataclasses import dataclass
from datetime import datetime

from core.domain import EventSeverity
from notifications.domain.generator import NotificationGenerator
from notifications.app import (
    SendEventAlertUseCase, SendEventAlertCommand,
    SendTimeoutAlertUseCase, SendTimeoutAlertCommand,
    SendSourceDiscoveredUseCase, SendSourceDiscoveredCommand,
    SendSourceDownUseCase, SendSourceDownCommand,
)


_SEVERITY_EMOJI = {
    EventSeverity.INFO: "ℹ️",
    EventSeverity.WARNING: "⚠️",
    EventSeverity.ERROR: "🔴",
    EventSeverity.CRITICAL: "🚨",
}


class DefaultGenerator(NotificationGenerator):
    """
    Ships with the template.  Produces clean Telegram HTML messages.
    Override any method to customise specific message types.
    """

    def _ts(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M UTC")

    def format_event_alert(self, source_name, severity, title, detail) -> str:
        emoji = _SEVERITY_EMOJI.get(severity, "•")
        text = (
            f"{emoji} <b>{source_name}</b> | {severity.upper()}\n\n"
            f"<b>{title}</b>"
        )
        if detail:
            text += f"\n<code>{detail}</code>"
        return text

    def format_timeout_alert(self, source_name, last_seen) -> str:
        return (
            f"⏰ <b>{source_name}</b> | No events detected\n\n"
            f"Last seen: <code>{self._ts(last_seen)}</code>\n"
            f"The source appears to be silent within its active window."
        )

    def format_source_discovered(self, source_name, discovered_at) -> str:
        return (
            f"🆕 <b>{source_name}</b> came online\n"
            f"First event at <code>{self._ts(discovered_at)}</code>"
        )

    def format_source_down(self, source_name, stopped_at) -> str:
        return (
            f"🔴 <b>{source_name}</b> is now inactive\n"
            f"Stopped at <code>{self._ts(stopped_at)}</code>"
        )


# ── Schemas ────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True, kw_only=True)
class EventAlertSchema:
    source_id: str
    source_name: str
    severity: EventSeverity
    title: str
    detail: str | None
    timestamp: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeoutAlertSchema:
    source_id: str
    source_name: str
    last_seen: datetime
    detected_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceDiscoveredSchema:
    source_id: str
    source_name: str
    discovered_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceDownSchema:
    source_id: str
    source_name: str
    stopped_at: datetime


# ── Facade ─────────────────────────────────────────────────────────────────

class AlertsFacade:
    def __init__(
        self,
        send_event_alert_uc: SendEventAlertUseCase,
        send_timeout_alert_uc: SendTimeoutAlertUseCase,
        send_source_discovered_uc: SendSourceDiscoveredUseCase,
        send_source_down_uc: SendSourceDownUseCase,
    ) -> None:
        self._send_event_alert_uc = send_event_alert_uc
        self._send_timeout_alert_uc = send_timeout_alert_uc
        self._send_source_discovered_uc = send_source_discovered_uc
        self._send_source_down_uc = send_source_down_uc

    async def notify_event_detected(self, schema: EventAlertSchema) -> None:
        await self._send_event_alert_uc(SendEventAlertCommand(
            source_name=schema.source_name,
            severity=schema.severity,
            title=schema.title,
            detail=schema.detail,
            timestamp=schema.timestamp,
        ))

    async def notify_timeout(self, schema: TimeoutAlertSchema) -> None:
        await self._send_timeout_alert_uc(SendTimeoutAlertCommand(
            source_name=schema.source_name,
            last_seen=schema.last_seen,
            detected_at=schema.detected_at,
        ))

    async def notify_source_discovered(self, schema: SourceDiscoveredSchema) -> None:
        await self._send_source_discovered_uc(SendSourceDiscoveredCommand(
            source_name=schema.source_name,
            discovered_at=schema.discovered_at,
        ))

    async def notify_source_down(self, schema: SourceDownSchema) -> None:
        await self._send_source_down_uc(SendSourceDownCommand(
            source_name=schema.source_name,
            stopped_at=schema.stopped_at,
        ))
