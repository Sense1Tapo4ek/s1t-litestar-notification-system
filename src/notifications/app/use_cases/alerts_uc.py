"""
Alert use cases.  Each UC fetches the appropriate filtered subscriber list
and broadcasts a formatted message using a NotificationGenerator.
"""
from dataclasses import dataclass
from datetime import datetime
import logging

from shared.generics import EventSeverity
from notifications.app.interfaces.i_subscriber_repo import ISubscriberRepo
from notifications.app.interfaces.i_telegram_gateway import ITelegramGateway
from notifications.domain import TelegramSubscriberEnt, NotificationGenerator

logger = logging.getLogger(__name__)


async def _broadcast(
    gateway: ITelegramGateway | None,
    subscribers: list[TelegramSubscriberEnt],
    text: str,
) -> None:
    if gateway is None:
        logger.debug("Telegram gateway not configured -- skipping broadcast")
        return
    for sub in subscribers:
        try:
            ok = await gateway.send_message(sub.chat_id, text)
            if not ok:
                logger.warning("Failed to deliver message to %s (@%s)", sub.chat_id, sub.username)
        except Exception:
            logger.exception("Error sending message to %s", sub.chat_id)


# ── Commands ────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True, kw_only=True)
class SendEventAlertCommand:
    source_name: str
    severity: EventSeverity
    title: str
    detail: str | None
    timestamp: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SendTimeoutAlertCommand:
    source_name: str
    last_seen: datetime
    detected_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SendSourceDiscoveredCommand:
    source_name: str
    discovered_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SendSourceDownCommand:
    source_name: str
    stopped_at: datetime


# ── Use Cases ───────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True, kw_only=True)
class SendEventAlertUseCase:
    _repo: ISubscriberRepo
    _gateway: ITelegramGateway
    _generator: "NotificationGenerator"

    async def __call__(self, cmd: SendEventAlertCommand) -> None:
        subs = await self._repo.get_active_for_events()
        text = self._generator.format_event_alert(
            source_name=cmd.source_name,
            severity=cmd.severity,
            title=cmd.title,
            detail=cmd.detail,
        )
        await _broadcast(self._gateway, subs, text)


@dataclass(frozen=True, slots=True, kw_only=True)
class SendTimeoutAlertUseCase:
    _repo: ISubscriberRepo
    _gateway: ITelegramGateway
    _generator: "NotificationGenerator"

    async def __call__(self, cmd: SendTimeoutAlertCommand) -> None:
        subs = await self._repo.get_active_for_timeouts()
        text = self._generator.format_timeout_alert(
            source_name=cmd.source_name,
            last_seen=cmd.last_seen,
        )
        await _broadcast(self._gateway, subs, text)


@dataclass(frozen=True, slots=True, kw_only=True)
class SendSourceDiscoveredUseCase:
    _repo: ISubscriberRepo
    _gateway: ITelegramGateway
    _generator: "NotificationGenerator"

    async def __call__(self, cmd: SendSourceDiscoveredCommand) -> None:
        subs = await self._repo.get_active_for_services()
        text = self._generator.format_source_discovered(
            source_name=cmd.source_name,
            discovered_at=cmd.discovered_at,
        )
        await _broadcast(self._gateway, subs, text)


@dataclass(frozen=True, slots=True, kw_only=True)
class SendSourceDownUseCase:
    _repo: ISubscriberRepo
    _gateway: ITelegramGateway
    _generator: "NotificationGenerator"

    async def __call__(self, cmd: SendSourceDownCommand) -> None:
        subs = await self._repo.get_active_for_services()
        text = self._generator.format_source_down(
            source_name=cmd.source_name,
            stopped_at=cmd.stopped_at,
        )
        await _broadcast(self._gateway, subs, text)


