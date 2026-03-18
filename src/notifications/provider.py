import logging
from typing import Optional

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from notifications.app import (
    SendEventAlertUseCase, SendTimeoutAlertUseCase,
    SendSourceDiscoveredUseCase, SendSourceDownUseCase,
    RegisterSubscriberUseCase, ToggleSubscriberUseCase,
    UpdatePreferencesUseCase,
    UpdateConfigUseCase, TestTelegramUseCase,
    GetSubscribersQuery, GetSubscriberQuery,
    IConfigRepo, ISubscriberRepo, ITelegramGateway,
)
from notifications.ports.driven.repos.sqlite_config_repo import SqliteConfigRepo
from notifications.ports.driven.repos.sqlite_subscriber_repo import SqliteSubscriberRepo
from notifications.domain.generator import NotificationGenerator
from notifications.ports.driving.alerts_facade import AlertsFacade, DefaultGenerator
from notifications.ports.driving.api.admin_ui_facade import AdminUIFacade
from notifications.ports.driving.telegram_facade import NotificationsTelegramFacade

logger = logging.getLogger(__name__)


class NotificationsProvider(Provider):
    scope = Scope.REQUEST

    # ── Driven ports (repos) ────────────────────────────────────────────
    @provide
    def provide_config_repo(self, session: AsyncSession) -> IConfigRepo:
        return SqliteConfigRepo(session)

    @provide
    def provide_subscriber_repo(self, session: AsyncSession) -> ISubscriberRepo:
        return SqliteSubscriberRepo(session)

    # ── Telegram gateway (APP-scoped so the Bot instance is reused) ─────
    @provide(scope=Scope.APP)
    def provide_notification_generator(self) -> NotificationGenerator:
        return DefaultGenerator()

    @provide(scope=Scope.APP)
    def provide_telegram_gateway(self) -> Optional[ITelegramGateway]:
        """
        Returns None when no token is configured.
        Alert UCs should handle None gracefully.
        Will be replaced by a real AiogramGateway at runtime in telegram.py
        once a token is discovered.
        """
        return None

    # ── Alert use cases ─────────────────────────────────────────────────
    @provide
    def provide_send_event_alert_uc(
        self,
        repo: ISubscriberRepo,
        gateway: Optional[ITelegramGateway],
        generator: NotificationGenerator,
    ) -> SendEventAlertUseCase:
        return SendEventAlertUseCase(_repo=repo, _gateway=gateway, _generator=generator)

    @provide
    def provide_send_timeout_alert_uc(
        self,
        repo: ISubscriberRepo,
        gateway: Optional[ITelegramGateway],
        generator: NotificationGenerator,
    ) -> SendTimeoutAlertUseCase:
        return SendTimeoutAlertUseCase(_repo=repo, _gateway=gateway, _generator=generator)

    @provide
    def provide_send_source_discovered_uc(
        self,
        repo: ISubscriberRepo,
        gateway: Optional[ITelegramGateway],
        generator: NotificationGenerator,
    ) -> SendSourceDiscoveredUseCase:
        return SendSourceDiscoveredUseCase(_repo=repo, _gateway=gateway, _generator=generator)

    @provide
    def provide_send_source_down_uc(
        self,
        repo: ISubscriberRepo,
        gateway: Optional[ITelegramGateway],
        generator: NotificationGenerator,
    ) -> SendSourceDownUseCase:
        return SendSourceDownUseCase(_repo=repo, _gateway=gateway, _generator=generator)

    @provide
    def provide_alerts_facade(
        self,
        send_event: SendEventAlertUseCase,
        send_timeout: SendTimeoutAlertUseCase,
        send_discovered: SendSourceDiscoveredUseCase,
        send_down: SendSourceDownUseCase,
    ) -> AlertsFacade:
        return AlertsFacade(
            send_event_alert_uc=send_event,
            send_timeout_alert_uc=send_timeout,
            send_source_discovered_uc=send_discovered,
            send_source_down_uc=send_down,
        )

    # ── Other use cases ─────────────────────────────────────────────────
    @provide
    def provide_register_subscriber_uc(self, repo: ISubscriberRepo) -> RegisterSubscriberUseCase:
        return RegisterSubscriberUseCase(_repo=repo)

    @provide
    def provide_toggle_subscriber_uc(self, repo: ISubscriberRepo) -> ToggleSubscriberUseCase:
        return ToggleSubscriberUseCase(_repo=repo)

    @provide
    def provide_update_prefs_uc(self, repo: ISubscriberRepo) -> UpdatePreferencesUseCase:
        return UpdatePreferencesUseCase(_repo=repo)

    @provide
    def provide_update_config_uc(self, repo: IConfigRepo) -> UpdateConfigUseCase:
        return UpdateConfigUseCase(_repo=repo)

    @provide
    def provide_test_telegram_uc(
        self,
        repo: ISubscriberRepo,
        gateway: Optional[ITelegramGateway],
    ) -> TestTelegramUseCase:
        return TestTelegramUseCase(_repo=repo, _gateway=gateway)

    # ── Queries ─────────────────────────────────────────────────────────
    @provide
    def provide_get_subscribers_query(self, repo: ISubscriberRepo) -> GetSubscribersQuery:
        return GetSubscribersQuery(_repo=repo)

    @provide
    def provide_get_subscriber_query(self, repo: ISubscriberRepo) -> GetSubscriberQuery:
        return GetSubscriberQuery(_repo=repo)

    # ── Driving facades ─────────────────────────────────────────────────
    @provide
    def provide_admin_ui_facade(
        self,
        config_repo: IConfigRepo,
        update_config_uc: UpdateConfigUseCase,
        test_telegram_uc: TestTelegramUseCase,
        toggle_subscriber_uc: ToggleSubscriberUseCase,
        update_prefs_uc: UpdatePreferencesUseCase,
        get_subscribers_query: GetSubscribersQuery,
    ) -> AdminUIFacade:
        return AdminUIFacade(
            config_repo=config_repo,
            update_config_uc=update_config_uc,
            test_telegram_uc=test_telegram_uc,
            toggle_subscriber_uc=toggle_subscriber_uc,
            update_prefs_uc=update_prefs_uc,
            get_subscribers_query=get_subscribers_query,
        )

    @provide
    def provide_notifications_tg_facade(
        self,
        register_uc: RegisterSubscriberUseCase,
        get_subscriber_query: GetSubscriberQuery,
        update_prefs_uc: UpdatePreferencesUseCase,
    ) -> NotificationsTelegramFacade:
        return NotificationsTelegramFacade(
            register_uc=register_uc,
            get_subscriber_query=get_subscriber_query,
            update_prefs_uc=update_prefs_uc,
        )
