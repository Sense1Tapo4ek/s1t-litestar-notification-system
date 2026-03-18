from notifications.app import (
    UpdateConfigUseCase,
    TestTelegramUseCase, TestResult,
    ToggleSubscriberUseCase,
    UpdatePreferencesUseCase, UpdatePreferencesCommand,
    GetSubscribersQuery,
)
from notifications.app.interfaces.i_config_repo import IConfigRepo
from .schemas import SubscriberResponseSchema, TestResultSchema


class AdminUIFacade:
    def __init__(
        self,
        config_repo: IConfigRepo,
        update_config_uc: UpdateConfigUseCase,
        test_telegram_uc: TestTelegramUseCase,
        toggle_subscriber_uc: ToggleSubscriberUseCase,
        update_prefs_uc: UpdatePreferencesUseCase,
        get_subscribers_query: GetSubscribersQuery,
    ) -> None:
        self._config_repo = config_repo
        self._update_config_uc = update_config_uc
        self._test_telegram_uc = test_telegram_uc
        self._toggle_subscriber_uc = toggle_subscriber_uc
        self._update_prefs_uc = update_prefs_uc
        self._get_subscribers_query = get_subscribers_query

    async def is_bot_configured(self) -> bool:
        config = await self._config_repo.get()
        return config.is_configured

    async def update_token(self, token: str) -> None:
        await self._update_config_uc(token)

    async def test_connection(self) -> TestResultSchema:
        result: TestResult = await self._test_telegram_uc()
        return TestResultSchema(
            total=result.total,
            sent=result.sent,
            failed=result.failed,
            details=result.details,
        )

    async def toggle_subscriber(self, chat_id: int) -> bool:
        return await self._toggle_subscriber_uc(chat_id)

    async def update_preference(self, chat_id: int, field: str, value: bool) -> None:
        allowed = {"notify_events", "notify_timeouts", "notify_services"}
        if field not in allowed:
            raise ValueError(f"Unknown preference field: {field}")
        cmd = UpdatePreferencesCommand(
            chat_id=chat_id,
            **{field: value},
        )
        await self._update_prefs_uc(cmd)

    async def get_subscribers(self) -> list[SubscriberResponseSchema]:
        subs = await self._get_subscribers_query()
        return [
            SubscriberResponseSchema(
                chat_id=s.chat_id,
                username=s.username,
                is_active=s.is_active,
                notify_events=s.notify_events,
                notify_timeouts=s.notify_timeouts,
                notify_services=s.notify_services,
            )
            for s in subs
        ]
