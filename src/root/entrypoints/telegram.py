"""
Telegram polling entrypoint.

Runs as a background asyncio task (started in worker.py).
Polls for a bot token every 10 s; once found, starts aiogram polling.
Restarts automatically if the token changes or polling crashes.
"""
import asyncio
import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from dishka import AsyncContainer

from core.adapters.driving.telegram import handlers as core_handlers
from notifications.adapters.driven.gateways.aiogram_gateway import AiogramGateway, TelegramGatewayRef
from notifications.adapters.driving.telegram import handlers as notif_handlers
from notifications.app.interfaces.i_config_repo import IConfigRepo

logger = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand(command="start", description="Subscribe to notifications"),
    BotCommand(command="sources", description="List all event sources"),
    BotCommand(command="stale", description="Show inactive sources"),
    BotCommand(command="settings", description="Notification preferences"),
]


class _PollingHandle:
    def __init__(self, dp: Dispatcher, bot: Bot) -> None:
        self._dp = dp
        self._bot = bot
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(
            self._dp.start_polling(self._bot, handle_signals=False),
            name="telegram-polling",
        )

    async def stop(self) -> None:
        await self._dp.stop_polling()
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

    async def get_token(self) -> Optional[str]:
        try:
            info = await self._bot.get_me()
            return info.username
        except Exception:
            return None


async def telegram_supervisor(container: AsyncContainer) -> None:
    current_token: Optional[str] = None
    handle: Optional[_PollingHandle] = None
    gateway_ref: TelegramGatewayRef = await container.get(TelegramGatewayRef)

    async def stop_current() -> None:
        nonlocal handle
        if handle:
            await handle.stop()
            handle = None
        gateway_ref.set(None)

    while True:
        try:
            async with container() as request_container:
                repo: IConfigRepo = await request_container.get(IConfigRepo)
                config = await repo.get()

            token = config.bot_token if config.is_configured else None

            if token != current_token:
                await stop_current()
                current_token = token

                if token:
                    logger.info("Telegram: starting polling with new token")
                    dp = Dispatcher()
                    dp.include_router(notif_handlers.router)
                    dp.include_router(core_handlers.router)

                    bot = Bot(
                        token=token,
                        default=DefaultBotProperties(parse_mode="HTML"),
                    )
                    await bot.set_my_commands(BOT_COMMANDS)
                    logger.info("Bot commands registered")

                    gateway_ref.set(AiogramGateway(bot))

                    from dishka.integrations.aiogram import setup_dishka as setup_aiogram_dishka
                    setup_aiogram_dishka(container=container, router=dp)

                    handle = _PollingHandle(dp, bot)
                    handle.start()
                else:
                    logger.info("Telegram: no token configured, polling paused")

            await asyncio.sleep(10)

        except asyncio.CancelledError:
            logger.info("Telegram supervisor cancelled")
            await stop_current()
            break
        except Exception:
            logger.exception("Telegram supervisor error")
            await asyncio.sleep(10)
