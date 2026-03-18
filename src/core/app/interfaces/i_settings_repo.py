from datetime import time
from typing import Protocol, Optional


class IGlobalSettingsRepo(Protocol):
    async def get_active_window(self) -> tuple[Optional[time], Optional[time]]: ...
    async def set_active_window(self, start: Optional[time], end: Optional[time]) -> None: ...
