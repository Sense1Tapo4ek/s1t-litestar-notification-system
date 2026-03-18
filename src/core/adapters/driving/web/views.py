from typing import Any, Optional
from litestar import get, post
from litestar.connection import Request
from litestar.controller import Controller
from litestar.response import Template, Redirect
from litestar.exceptions import NotFoundException
from dishka.integrations.litestar import FromDishka, inject

from core.ports.driving.source_ui_facade import SourceUIFacade


def _flash(request: Request) -> dict:
    return {
        "flash_msg": request.query_params.get("msg"),
        "flash_error": request.query_params.get("error"),
    }


class SourceController(Controller):
    path = "/"

    @get("/", name="dashboard")
    @inject
    async def dashboard(
        self,
        request: Request,
        facade: FromDishka[SourceUIFacade],
    ) -> Template:
        sources = await facade.get_dashboard()
        global_settings = await facade.get_global_settings()
        return Template(
            "dashboard.html",
            context={"sources": sources, "global_settings": global_settings, **_flash(request)},
        )

    @post("/settings", name="update_global_settings")
    @inject
    async def update_global_settings(
        self,
        facade: FromDishka[SourceUIFacade],
        data: dict[str, Any],
    ) -> Redirect:
        await facade.update_global_settings(
            active_window_start=data.get("active_window_start") or None,
            active_window_end=data.get("active_window_end") or None,
        )
        return Redirect(path="/?msg=Active+window+saved")

    @get("/sources/{source_id:str}", name="source_details")
    @inject
    async def source_details(
        self,
        source_id: str,
        request: Request,
        facade: FromDishka[SourceUIFacade],
    ) -> Template:
        details = await facade.get_source_details(source_id)
        if not details:
            raise NotFoundException(detail=f"Source '{source_id}' not found")
        return Template(
            "source_details.html",
            context={"source": details, **_flash(request)},
        )

    @post("/sources/{source_id:str}/settings", name="update_source_settings")
    @inject
    async def update_source_settings(
        self,
        source_id: str,
        facade: FromDishka[SourceUIFacade],
        data: dict[str, Any],
    ) -> Redirect:
        await facade.update_settings(
            source_id=source_id,
            custom_name=data.get("custom_name") or None,
            notify_events="notify_events" in data,
            active_window_start=data.get("active_window_start") or None,
            active_window_end=data.get("active_window_end") or None,
        )
        return Redirect(path=f"/sources/{source_id}?msg=Settings+saved")

    @post("/sources/{source_id:str}/clear", name="clear_source_history")
    @inject
    async def clear_source_history(
        self,
        source_id: str,
        facade: FromDishka[SourceUIFacade],
    ) -> Redirect:
        await facade.clear_history(source_id)
        return Redirect(path=f"/sources/{source_id}?msg=History+cleared")

    @post("/sources/{source_id:str}/remove", name="remove_source")
    @inject
    async def remove_source(
        self,
        source_id: str,
        facade: FromDishka[SourceUIFacade],
    ) -> Redirect:
        await facade.remove_source(source_id)
        return Redirect(path="/?msg=Source+removed")
