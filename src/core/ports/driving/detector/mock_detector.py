"""
MockDetector -- ships with the template to make the UI live out-of-the-box.

Registers three fake sources and emits random events every 5-15 seconds.
Approximately every 60 seconds it briefly marks one source "down" and
brings it back after 20 seconds, which fires service-down alerts if Telegram
is configured.

Replace this with your own NotificationDetector subclass in worker.py.
"""
import asyncio
import logging
import random
from datetime import datetime, timezone
from uuid import uuid4

from core.domain import EventSeverity
from .base_detector import NotificationDetector, OnEventCallback

logger = logging.getLogger(__name__)

_SOURCES = [
    ("payment-service", "Payment Service"),
    ("email-worker", "Email Worker"),
    ("data-pipeline", "Data Pipeline"),
]

_EVENTS = [
    (EventSeverity.INFO, "Heartbeat OK", None),
    (EventSeverity.INFO, "Processed batch", "batch_size=250 items"),
    (EventSeverity.INFO, "Health check passed", None),
    (EventSeverity.WARNING, "Response latency elevated", "p99=320ms (threshold=300ms)"),
    (EventSeverity.WARNING, "Queue depth growing", "depth=1 200, consumer_lag=8.4s"),
    (EventSeverity.WARNING, "Retry attempt", "attempt=2/3 on request #4417"),
    (EventSeverity.ERROR, "Dependency timeout", "upstream=db-primary timeout=5s"),
    (EventSeverity.ERROR, "Failed to send email", "recipient=user@example.com reason=SMTP reject"),
    (EventSeverity.CRITICAL, "Out of memory", "heap_used=97% pid=1337"),
]


class MockDetector(NotificationDetector):
    """Generates fake events on a timer for demo / development purposes."""

    def __init__(self) -> None:
        self._stop_event = asyncio.Event()
        self._down_source: str | None = None

    async def run(self, on_event: OnEventCallback) -> None:
        logger.info("MockDetector started -- will emit events every 5-15 s for %d sources", len(_SOURCES))
        tick = 0
        while not self._stop_event.is_set():
            await asyncio.sleep(random.uniform(5, 15))
            if self._stop_event.is_set():
                break

            source_id, source_name = random.choice(_SOURCES)
            severity, title, detail = random.choice(_EVENTS)

            ts = datetime.now(timezone.utc)
            await on_event(source_id, str(uuid4()), severity, title, detail, ts)

            tick += 1
            if tick % 8 == 0:
                await self._simulate_down_up(on_event)

        logger.info("MockDetector stopped")

    async def _simulate_down_up(self, on_event: OnEventCallback) -> None:
        source_id, source_name = random.choice(_SOURCES)
        ts = datetime.now(timezone.utc)
        await on_event(
            source_id, str(uuid4()), EventSeverity.CRITICAL,
            f"{source_name} appears unresponsive",
            "No events received within expected window; marking as down.",
            ts,
        )
        logger.info("MockDetector: simulated source down -- %s", source_id)

    async def stop(self) -> None:
        self._stop_event.set()
