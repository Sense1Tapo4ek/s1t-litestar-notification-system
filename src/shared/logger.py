import asyncio
import logging
import sys
import time
from .config import GenericConfig

SLOW_CALLBACK_THRESHOLD = 0.3


def setup_logging(config: GenericConfig) -> None:
    logging.basicConfig(
        level=config.log_level,
        format="%(levelname)s - %(asctime)s - %(name)s - %(funcName)s - %(message)s",
        stream=sys.stdout,
        force=True,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def enable_slow_callback_logging() -> None:
    loop = asyncio.get_running_loop()
    loop.slow_callback_duration = SLOW_CALLBACK_THRESHOLD
    loop.set_debug(True)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("EventLoopHealth").info(
        f"Slow callback detector enabled (threshold={SLOW_CALLBACK_THRESHOLD}s)"
    )


async def event_loop_health_ticker(interval: float = 30.0) -> None:
    logger = logging.getLogger("EventLoopHealth")
    try:
        while True:
            t0 = time.monotonic()
            await asyncio.sleep(interval)
            lag = time.monotonic() - t0 - interval
            if lag > 1.0:
                logger.warning(f"Event loop lag: {lag:.3f}s")
            elif lag > 0.3:
                logger.info(f"Event loop lag: {lag:.3f}s")
    except asyncio.CancelledError:
        pass
