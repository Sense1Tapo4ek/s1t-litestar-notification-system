from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.app import (
    ProcessEventUseCase, AddSourceUseCase, RemoveSourceUseCase,
    UpdateSourceSettingsUseCase, ClearSourceHistoryUseCase,
    MarkSourceActiveUseCase, MarkSourceInactiveUseCase,
    CheckTimeoutsUseCase, TickHealthUseCase,
    GetGlobalSettingsQuery, UpdateGlobalSettingsUseCase,
    GetDashboardQuery, GetSourceDetailsQuery, GetSourceStatsQuery,
    GetActiveSourcesListQuery, GetInactiveSourcesListQuery,
    IEventLogRepo, INotificationGateway, IGlobalSettingsRepo,
)
from core.ports.driven.repos.sqlite_event_log_repo import SqliteEventLogRepo
from core.ports.driven.repos.sqlite_settings_repo import SqliteGlobalSettingsRepo
from core.ports.driven.notification_acl import NotificationACL
from core.ports.driving.source_ui_facade import SourceUIFacade
from core.ports.driving.telegram.telegram_facade import CoreTelegramFacade
from notifications.ports.driving.alerts_facade import AlertsFacade


class CoreProvider(Provider):
    scope = Scope.REQUEST

    # ── Driven ports (repos) ────────────────────────────────────────────
    @provide
    def provide_event_log_repo(self, session: AsyncSession) -> IEventLogRepo:
        return SqliteEventLogRepo(session)

    @provide
    def provide_settings_repo(self, session: AsyncSession) -> IGlobalSettingsRepo:
        return SqliteGlobalSettingsRepo(session)

    @provide
    def provide_notification_gateway(self, alerts_facade: AlertsFacade) -> INotificationGateway:
        return NotificationACL(alerts_facade)

    # ── Use cases ───────────────────────────────────────────────────────
    @provide
    def provide_process_event_uc(self, repo: IEventLogRepo, notifier: INotificationGateway) -> ProcessEventUseCase:
        return ProcessEventUseCase(_repo=repo, _notifier=notifier)

    @provide
    def provide_add_source_uc(self, repo: IEventLogRepo) -> AddSourceUseCase:
        return AddSourceUseCase(_repo=repo)

    @provide
    def provide_remove_source_uc(self, repo: IEventLogRepo) -> RemoveSourceUseCase:
        return RemoveSourceUseCase(_repo=repo)

    @provide
    def provide_update_settings_uc(self, repo: IEventLogRepo) -> UpdateSourceSettingsUseCase:
        return UpdateSourceSettingsUseCase(_repo=repo)

    @provide
    def provide_clear_history_uc(self, repo: IEventLogRepo) -> ClearSourceHistoryUseCase:
        return ClearSourceHistoryUseCase(_repo=repo)

    @provide
    def provide_mark_active_uc(self, repo: IEventLogRepo, notifier: INotificationGateway) -> MarkSourceActiveUseCase:
        return MarkSourceActiveUseCase(_repo=repo, _notifier=notifier)

    @provide
    def provide_mark_inactive_uc(self, repo: IEventLogRepo, notifier: INotificationGateway) -> MarkSourceInactiveUseCase:
        return MarkSourceInactiveUseCase(_repo=repo, _notifier=notifier)

    @provide
    def provide_check_timeouts_uc(self, repo: IEventLogRepo, notifier: INotificationGateway) -> CheckTimeoutsUseCase:
        return CheckTimeoutsUseCase(_repo=repo, _notifier=notifier)

    @provide
    def provide_tick_health_uc(self, repo: IEventLogRepo) -> TickHealthUseCase:
        return TickHealthUseCase(_repo=repo)

    @provide
    def provide_global_settings_query(self, repo: IGlobalSettingsRepo) -> GetGlobalSettingsQuery:
        return GetGlobalSettingsQuery(_repo=repo)

    @provide
    def provide_update_global_settings_uc(self, repo: IGlobalSettingsRepo) -> UpdateGlobalSettingsUseCase:
        return UpdateGlobalSettingsUseCase(_repo=repo)

    # ── Queries ─────────────────────────────────────────────────────────
    @provide
    def provide_dashboard_query(self, repo: IEventLogRepo) -> GetDashboardQuery:
        return GetDashboardQuery(_repo=repo)

    @provide
    def provide_source_details_query(self, repo: IEventLogRepo) -> GetSourceDetailsQuery:
        return GetSourceDetailsQuery(_repo=repo)

    @provide
    def provide_source_stats_query(self, repo: IEventLogRepo) -> GetSourceStatsQuery:
        return GetSourceStatsQuery(_repo=repo)

    @provide
    def provide_active_sources_query(self, repo: IEventLogRepo) -> GetActiveSourcesListQuery:
        return GetActiveSourcesListQuery(_repo=repo)

    @provide
    def provide_inactive_sources_query(self, repo: IEventLogRepo) -> GetInactiveSourcesListQuery:
        return GetInactiveSourcesListQuery(_repo=repo)

    # ── Driving ports (facades) ─────────────────────────────────────────
    @provide
    def provide_source_ui_facade(
        self,
        dashboard_query: GetDashboardQuery,
        source_details_query: GetSourceDetailsQuery,
        source_stats_query: GetSourceStatsQuery,
        update_settings_uc: UpdateSourceSettingsUseCase,
        clear_history_uc: ClearSourceHistoryUseCase,
        remove_source_uc: RemoveSourceUseCase,
        global_settings_query: GetGlobalSettingsQuery,
        update_global_settings_uc: UpdateGlobalSettingsUseCase,
    ) -> SourceUIFacade:
        return SourceUIFacade(
            dashboard_query=dashboard_query,
            source_details_query=source_details_query,
            source_stats_query=source_stats_query,
            update_settings_uc=update_settings_uc,
            clear_history_uc=clear_history_uc,
            remove_source_uc=remove_source_uc,
            global_settings_query=global_settings_query,
            update_global_settings_uc=update_global_settings_uc,
        )

    @provide
    def provide_core_tg_facade(
        self,
        dashboard_query: GetDashboardQuery,
        source_stats_query: GetSourceStatsQuery,
    ) -> CoreTelegramFacade:
        return CoreTelegramFacade(
            dashboard_query=dashboard_query,
            source_stats_query=source_stats_query,
        )
