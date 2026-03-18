import asyncio
import logging
from pathlib import Path

from litestar import Litestar, get
from litestar.config.response_cache import ResponseCacheConfig
from litestar.static_files import create_static_files_router
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.response import Response
from dishka.integrations.litestar import setup_dishka

from core.adapters.driving.web.views import SourceController
from notifications.adapters.driving.web.views import AdminController
from root.container import build_container
from shared.config import GenericConfig
from shared.logger import setup_logging, enable_slow_callback_logging, event_loop_health_ticker

logger = logging.getLogger(__name__)
_BASE = Path(__file__).parent.parent.parent

_health_task: asyncio.Task | None = None
_worker_task: asyncio.Task | None = None
_container = None


@get("/health", sync_to_thread=False)
def health() -> Response:
    return Response(content={"status": "ok"})


async def on_startup() -> None:
    global _health_task, _worker_task
    try:
        enable_slow_callback_logging()
    except RuntimeError:
        pass
    _health_task = asyncio.create_task(event_loop_health_ticker(), name="event-loop-health")

    from root.entrypoints.worker import worker_loop
    _worker_task = asyncio.create_task(worker_loop(_container), name="worker-loop")
    logger.info("Application started")


async def on_shutdown() -> None:
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await asyncio.wait_for(_worker_task, timeout=15.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
    if _health_task and not _health_task.done():
        _health_task.cancel()
        try:
            await asyncio.wait_for(_health_task, timeout=2.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
    logger.info("Application stopped")


def create_app() -> Litestar:
    global _container
    config = GenericConfig()
    setup_logging(config)

    _container = build_container()
    container = _container

    static_router = create_static_files_router(
        path="/static",
        directories=[str(_BASE / "shared" / "static")],
    )

    app = Litestar(
        route_handlers=[
            health,
            SourceController,
            AdminController,
            static_router,
        ],
        template_config=TemplateConfig(
            directory=_BASE / "shared" / "templates",
            engine=JinjaTemplateEngine,
        ),
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
        response_cache_config=ResponseCacheConfig(),
        debug=False,
    )

    setup_dishka(container=container, app=app)
    return app
