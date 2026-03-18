from dataclasses import dataclass
from datetime import time
from typing import Optional, Tuple

from ..interfaces.i_settings_repo import IGlobalSettingsRepo


@dataclass(frozen=True, slots=True, kw_only=True)
class GetGlobalSettingsQuery:
    _repo: IGlobalSettingsRepo

    async def __call__(self) -> Tuple[Optional[time], Optional[time]]:
        return await self._repo.get_active_window()


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateGlobalSettingsUseCase:
    _repo: IGlobalSettingsRepo

    async def __call__(self, start: Optional[time], end: Optional[time]) -> None:
        await self._repo.set_active_window(start, end)
