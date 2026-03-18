import logging
from dataclasses import dataclass
from typing import Optional

from notifications.app.interfaces.i_config_repo import IConfigRepo
from notifications.app.interfaces.i_subscriber_repo import ISubscriberRepo
from notifications.app.interfaces.i_telegram_gateway import ITelegramGateway

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateConfigUseCase:
    _repo: IConfigRepo

    async def __call__(self, bot_token: str) -> None:
        config = await self._repo.get()
        config.set_token(bot_token)
        await self._repo.save(config)
        logger.info("Telegram config updated (token set)")


@dataclass(frozen=True, slots=True, kw_only=True)
class TestResult:
    total: int
    sent: int
    failed: int
    details: list[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class TestTelegramUseCase:
    _repo: ISubscriberRepo
    _gateway: ITelegramGateway

    async def __call__(self) -> TestResult:
        subscribers = await self._repo.get_active()
        total = len(subscribers)
        sent = 0
        failed = 0
        details: list[str] = []

        if not subscribers:
            logger.info("TestTelegram: no active subscribers to send to")
            return TestResult(total=0, sent=0, failed=0, details=["No active subscribers"])

        for sub in subscribers:
            msg = (
                f"✅ <b>Test message</b>\n"
                f"Notification system is operational.\n"
                f"Subscriber: @{sub.username}"
            )
            try:
                ok = await self._gateway.send_message(sub.chat_id, msg)
                if ok:
                    sent += 1
                    details.append(f"✅ Sent to @{sub.username} ({sub.chat_id})")
                else:
                    failed += 1
                    details.append(f"❌ Failed to deliver to @{sub.username} ({sub.chat_id})")
            except Exception as exc:
                failed += 1
                details.append(f"❌ Error for @{sub.username}: {exc}")
                logger.exception("TestTelegram: error sending to %s", sub.chat_id)

        logger.info("TestTelegram: sent=%d failed=%d total=%d", sent, failed, total)
        return TestResult(total=total, sent=sent, failed=failed, details=details)
