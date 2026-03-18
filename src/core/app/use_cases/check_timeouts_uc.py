from dataclasses import dataclass
from datetime import datetime

from ..interfaces.i_event_log_repo import IEventLogRepo
from ..interfaces.i_notification_gateway import INotificationGateway


@dataclass(frozen=True, slots=True, kw_only=True)
class CheckTimeoutsUseCase:
    """
    Runs periodically (from the background worker).
    For each active source with a configured active_window, checks if it has
    been silent longer than the timeout threshold and sends an alert.
    """
    _repo: IEventLogRepo
    _notifier: INotificationGateway

    async def __call__(self) -> None:
        sources = await self._repo.get_all_active()
        current_ts = datetime.now()
        for source in sources:
            event = source.check_timeout(current_ts=current_ts)
            if event is not None:
                await self._notifier.send_timeout_alert(event)
