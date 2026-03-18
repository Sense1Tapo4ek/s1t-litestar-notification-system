from dataclasses import dataclass
from datetime import datetime

from ..interfaces.i_event_log_repo import IEventLogRepo


@dataclass(frozen=True, slots=True, kw_only=True)
class TickHealthCommand:
    source_id: str
    timestamp: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class TickHealthUseCase:
    """Updates last_seen_ts for a source without loading the full aggregate."""
    _repo: IEventLogRepo

    async def __call__(self, cmd: TickHealthCommand) -> None:
        await self._repo.update_last_seen(cmd.source_id, cmd.timestamp)
