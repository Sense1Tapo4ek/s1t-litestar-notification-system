"""
Notifications context Telegram handlers -- /start, /settings.
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dishka.integrations.aiogram import FromDishka, inject

from notifications.ports.driving.telegram_facade import NotificationsTelegramFacade

logger = logging.getLogger(__name__)
router = Router(name="notifications")


def _prefs_keyboard(sub) -> InlineKeyboardMarkup:
    def btn(label: str, field: str, current: bool) -> InlineKeyboardButton:
        icon = "✅" if current else "❌"
        return InlineKeyboardButton(
            text=f"{icon} {label}",
            callback_data=f"pref:{field}:{int(not current)}",
        )

    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Events", "notify_events", sub.notify_events)],
        [btn("Timeouts", "notify_timeouts", sub.notify_timeouts)],
        [btn("Services", "notify_services", sub.notify_services)],
    ])


@router.message(Command("start"))
@inject
async def cmd_start(message: Message, facade: FromDishka[NotificationsTelegramFacade]) -> None:
    chat_id = message.from_user.id
    username = message.from_user.username or str(chat_id)
    logger.info("/start received from %s (@%s)", chat_id, username)
    try:
        await facade.register(chat_id=chat_id, username=username)
        await message.reply(
            f"👋 Hello, @{username}!\n\n"
            "You are now subscribed to notifications.\n\n"
            "Commands:\n"
            "/sources — list event sources\n"
            "/stale — show inactive sources\n"
            "/settings — manage notification preferences\n",
        )
    except Exception:
        logger.exception("/start handler failed for %s", chat_id)
        await message.reply("An error occurred. Please try again.")


@router.message(Command("settings"))
@inject
async def cmd_settings(message: Message, facade: FromDishka[NotificationsTelegramFacade]) -> None:
    chat_id = message.from_user.id
    try:
        sub = await facade.get_subscriber(chat_id)
        if not sub:
            await message.reply("You are not subscribed. Use /start to subscribe.")
            return
        await message.reply(
            "⚙️ <b>Notification preferences</b>\nTap a button to toggle:",
            parse_mode="HTML",
            reply_markup=_prefs_keyboard(sub),
        )
    except Exception:
        logger.exception("/settings handler failed for %s", chat_id)
        await message.reply("An error occurred. Please try again.")


@router.callback_query(F.data.startswith("pref:"))
@inject
async def handle_pref_toggle(
    query: CallbackQuery,
    facade: FromDishka[NotificationsTelegramFacade],
) -> None:
    chat_id = query.from_user.id
    try:
        _, field, raw_value = query.data.split(":")
        value = bool(int(raw_value))
        await facade.toggle_preference(chat_id=chat_id, field=field, value=value)
        sub = await facade.get_subscriber(chat_id)
        if sub:
            await query.message.edit_reply_markup(reply_markup=_prefs_keyboard(sub))
        await query.answer("Preference updated.")
    except Exception:
        logger.exception("pref toggle failed for %s", chat_id)
        await query.answer("Error updating preference.")
