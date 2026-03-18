"""
Background worker.

Responsibilities:
1. Run the NotificationDetector (MockDetector by default).
2. Periodically check for source timeouts.
3. Run the Telegram polling supervisor.
"""
import asyncio
import logging
from dishka import AsyncContainer

from core.app import CheckTimeoutsUseCase, AddSourceUseCase, ProcessEventUseCase
from core.ports.driving.detector.mock_detector import MockDetector
from core.ports.driving.detector.detector_manager import DetectorManager
from root.entrypoints.telegram import telegram_supervisor

logger = logging.getLogger(__name__)

WORKER_INTERVAL_SECONDS = 30
_telegram_task: asyncio.Task | None = None


async def _check_timeouts(container: AsyncContainer) -> None:
    try:
        async with container() as rc:
            uc: CheckTimeoutsUseCase = await rc.get(CheckTimeoutsUseCase)
            await uc()
    except Exception:
        logger.exception("check_timeouts failed")


async def worker_loop(container: AsyncContainer) -> None:
    global _telegram_task
    logger.info("Worker started")

    async with container() as rc:
        add_source_uc: AddSourceUseCase = await rc.get(AddSourceUseCase)
        process_event_uc: ProcessEventUseCase = await rc.get(ProcessEventUseCase)

    detector = MockDetector()
    manager = DetectorManager(
        detector=detector,
        process_event_uc=process_event_uc,
        add_source_uc=add_source_uc,
    )
    manager.start()

    _telegram_task = asyncio.create_task(
        telegram_supervisor(container), name="telegram-supervisor"
    )

    tick = 0
    try:
        while True:
            await asyncio.sleep(WORKER_INTERVAL_SECONDS)
            tick += 1
            await _check_timeouts(container)
    except asyncio.CancelledError:
        logger.info("Worker loop cancelled, shutting down")
    finally:
        await manager.stop()
        if _telegram_task and not _telegram_task.done():
            _telegram_task.cancel()
            try:
                await asyncio.wait_for(_telegram_task, timeout=8.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        logger.info("Worker stopped")
