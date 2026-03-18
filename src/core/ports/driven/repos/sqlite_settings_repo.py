from datetime import time
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.adapters.driven.db.orm_models import GlobalSettingsModel
from core.app.interfaces.i_settings_repo import IGlobalSettingsRepo


_KEY_START = "active_window_start"
_KEY_END = "active_window_end"


def _parse_time(value: Optional[str]) -> Optional[time]:
    if not value:
        return None
    try:
        parts = value.split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


class SqliteGlobalSettingsRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get(self, key: str) -> Optional[str]:
        model = await self._session.get(GlobalSettingsModel, key)
        return model.value if model else None

    async def _set(self, key: str, value: Optional[str]) -> None:
        model = GlobalSettingsModel(key=key, value=value)
        await self._session.merge(model)
        await self._session.commit()

    async def get_active_window(self) -> tuple[Optional[time], Optional[time]]:
        return (
            _parse_time(await self._get(_KEY_START)),
            _parse_time(await self._get(_KEY_END)),
        )

    async def set_active_window(self, start: Optional[time], end: Optional[time]) -> None:
        await self._set(_KEY_START, start.strftime("%H:%M") if start else None)
        await self._set(_KEY_END, end.strftime("%H:%M") if end else None)
