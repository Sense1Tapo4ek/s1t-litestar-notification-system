"""
DetectorManager -- bridges NotificationDetector → application use cases.

Responsibilities:
- Auto-registers sources when the detector first emits an event for them.
- Translates detector callbacks into ProcessEventCommand.
- Manages the asyncio Task lifecycle (start / stop).
"""
import asyncio
import logging
from datetime import datetime, timezone

from dishka import AsyncContainer

from core.app import (
    ProcessEventUseCase, ProcessEventCommand,
    AddSourceUseCase,
)
from core.domain import EventSeverity
from .base_detector import NotificationDetector, OnEventCallback

logger = logging.getLogger(__name__)


class DetectorManager:
    def __init__(
        self,
        detector: NotificationDetector,
        container: AsyncContainer,
    ) -> None:
        self._detector = detector
        self._container = container
        self._task: asyncio.Task | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._task = asyncio.create_task(
            self._run(), name="detector-manager"
        )
        logger.info("DetectorManager started")

    async def stop(self) -> None:
        await self._detector.stop()
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        logger.info("DetectorManager stopped")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _run(self) -> None:
        try:
            await self._detector.run(self._on_event)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Detector crashed")

    async def _on_event(
        self,
        source_id: str,
        event_id: str,
        severity: EventSeverity,
        title: str,
        detail: str | None,
        timestamp: datetime | None,
    ) -> None:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        try:
            async with self._container() as rc:
                add_source_uc: AddSourceUseCase = await rc.get(AddSourceUseCase)
                process_event_uc: ProcessEventUseCase = await rc.get(ProcessEventUseCase)
                await add_source_uc(source_id)
                cmd = ProcessEventCommand(
                    source_id=source_id,
                    event_id=event_id,
                    severity=severity,
                    title=title,
                    timestamp=timestamp,
                    detail=detail,
                )
                await process_event_uc(cmd)
        except Exception:
            logger.exception("DetectorManager: failed to process event from source %s", source_id)
