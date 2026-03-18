from typing import Optional
from notifications.app import (
    RegisterSubscriberUseCase,
    GetSubscriberQuery,
    UpdatePreferencesUseCase, UpdatePreferencesCommand,
)
from notifications.domain import TelegramSubscriberEnt


class NotificationsTelegramFacade:
    def __init__(
        self,
        register_uc: RegisterSubscriberUseCase,
        get_subscriber_query: GetSubscriberQuery,
        update_prefs_uc: UpdatePreferencesUseCase,
    ) -> None:
        self._register_uc = register_uc
        self._get_subscriber_query = get_subscriber_query
        self._update_prefs_uc = update_prefs_uc

    async def register(self, chat_id: int, username: str) -> None:
        await self._register_uc(chat_id=chat_id, username=username)

    async def get_subscriber(self, chat_id: int) -> Optional[TelegramSubscriberEnt]:
        return await self._get_subscriber_query(chat_id)

    async def toggle_preference(
        self,
        chat_id: int,
        field: str,
        value: bool,
    ) -> None:
        cmd = UpdatePreferencesCommand(chat_id=chat_id, **{field: value})
        await self._update_prefs_uc(cmd)
