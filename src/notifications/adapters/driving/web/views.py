from typing import Annotated, Any
from litestar import get, post
from litestar.connection import Request
from litestar.controller import Controller
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Template, Redirect
from dishka.integrations.litestar import FromDishka, inject

from notifications.ports.driving.api.admin_ui_facade import AdminUIFacade


def _flash(request: Request) -> dict:
    return {
        "flash_msg": request.query_params.get("msg"),
        "flash_error": request.query_params.get("error"),
    }


class AdminController(Controller):
    path = "/admin"

    @get("/", name="admin")
    @inject
    async def admin_page(
        self,
        request: Request,
        facade: FromDishka[AdminUIFacade],
    ) -> Template:
        subscribers = await facade.get_subscribers()
        is_configured = await facade.is_bot_configured()
        return Template(
            "admin.html",
            context={
                "subscribers": subscribers,
                "is_configured": is_configured,
                **_flash(request),
            },
        )

    @post("/token", name="update_token")
    @inject
    async def update_token(
        self,
        facade: FromDishka[AdminUIFacade],
        data: Annotated[dict[str, Any], Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        token = (data.get("token") or "").strip()
        if not token:
            return Redirect(path="/admin?error=Token+cannot+be+empty")
        await facade.update_token(token)
        return Redirect(path="/admin?msg=Token+saved+successfully")

    @post("/test", name="test_telegram")
    @inject
    async def test_connection(self, facade: FromDishka[AdminUIFacade]) -> Redirect:
        result = await facade.test_connection()
        msg = f"Sent+{result.sent}+of+{result.total}"
        return Redirect(path=f"/admin?msg={msg}")

    @post("/{chat_id:int}/toggle", name="toggle_subscriber")
    @inject
    async def toggle_subscriber(
        self, chat_id: int, facade: FromDishka[AdminUIFacade]
    ) -> Redirect:
        is_active = await facade.toggle_subscriber(chat_id)
        status = "activated" if is_active else "deactivated"
        return Redirect(path=f"/admin?msg=Subscriber+{status}")

    @post("/{chat_id:int}/preferences", name="update_preference")
    @inject
    async def update_preference(
        self,
        chat_id: int,
        facade: FromDishka[AdminUIFacade],
        data: Annotated[dict[str, Any], Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        field = data.get("field", "")
        value = data.get("value") == "1"
        try:
            await facade.update_preference(chat_id, field, value)
        except ValueError:
            return Redirect(path="/admin?error=Unknown+preference+field")
        return Redirect(path="/admin?msg=Preference+updated")
