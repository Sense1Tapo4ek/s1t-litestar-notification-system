"""
Core context Telegram handlers -- /sources and /stale commands.
"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from dishka.integrations.aiogram import FromDishka, inject

from core.ports.driving.telegram.telegram_facade import CoreTelegramFacade

logger = logging.getLogger(__name__)
router = Router(name="core")


def _fmt_ts(dt) -> str:
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _fmt_uptime(seconds: int | None) -> str:
    if seconds is None:
        return "N/A"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s"


@router.message(Command("sources"))
@inject
async def cmd_sources(message: Message, facade: FromDishka[CoreTelegramFacade]) -> None:
    try:
        sources = await facade.list_sources()
        if not sources:
            await message.reply("No sources registered yet.")
            return
        lines = ["<b>Event Sources</b>\n"]
        for s in sources:
            status = "🟢" if s.is_active else "🔴"
            lines.append(
                f"{status} <b>{s.display_name}</b>\n"
                f"   Events: {s.total_events} | Errors: {s.error_count}\n"
                f"   Last seen: {_fmt_ts(s.last_seen_ts)}\n"
            )
        await message.reply("\n".join(lines), parse_mode="HTML")
    except Exception:
        logger.exception("cmd_sources failed")
        await message.reply("An error occurred. Please try again.")


@router.message(Command("stale"))
@inject
async def cmd_stale(message: Message, facade: FromDishka[CoreTelegramFacade]) -> None:
    try:
        sources = await facade.list_sources()
        stale = [s for s in sources if not s.is_active]
        if not stale:
            await message.reply("All registered sources are currently active.")
            return
        lines = ["<b>Inactive Sources</b>\n"]
        for s in stale:
            lines.append(
                f"🔴 <b>{s.display_name}</b>\n"
                f"   Events: {s.total_events} | Errors: {s.error_count}\n"
                f"   Last seen: {_fmt_ts(s.last_seen_ts)}\n"
            )
        await message.reply("\n".join(lines), parse_mode="HTML")
    except Exception:
        logger.exception("cmd_stale failed")
        await message.reply("An error occurred. Please try again.")
