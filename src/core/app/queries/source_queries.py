from dataclasses import dataclass
from typing import Optional

from ...domain import EventLogAgg
from ..interfaces.i_event_log_repo import IEventLogRepo


@dataclass(frozen=True, slots=True, kw_only=True)
class GetSourceDetailsQuery:
    _repo: IEventLogRepo

    async def __call__(self, source_id: str) -> Optional[EventLogAgg]:
        return await self._repo.get_by_id(source_id)
