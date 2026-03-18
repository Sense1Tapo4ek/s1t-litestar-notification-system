# Architecture

This project follows **S-DDD (Structured Domain-Driven Design)** — a pragmatic layered architecture
that applies DDD principles within a strict port-and-adapter structure.

---

## Bounded Contexts

```
s1t-litestar-notification-system/
  src/
    core/           ← "Event Monitoring" context
    notifications/  ← "Telegram Notifications" context
    shared/         ← Cross-cutting: config, logging, DB session, static files
    root/           ← Composition root only (no business logic)
```

Each context owns its domain, application, ports, and adapters.
Contexts communicate via **facade interfaces** — never by sharing domain objects.

---

## Layer Rules

```
  Adapters (driving)     ← can only call → Ports (driving)
  Ports (driving)        ← can only call → App
  App                    ← can only call → Domain + Ports (driven interfaces)
  Ports (driven)         ← implements  → App interfaces; calls → Adapters (driven)
  Adapters (driven)      ← I/O only (DB, HTTP, etc.)
```

Import direction: **inward only**.  
Domain never imports App; App never imports Adapters.

---

## Data Flow

```
External Source
    │
    ▼
NotificationDetector.run()          ← user-subclassed ABC
    │  on_event(source_id, severity, title, ...)
    ▼
DetectorManager._on_event()
    │  auto-registers new sources via AddSourceUseCase
    │  ProcessEventCommand
    ▼
ProcessEventUseCase
    │  EventLogAgg.record_event() → EventDetectedEvent
    ▼
INotificationGateway (core interface)
    │
    ▼
NotificationACL  (Anti-Corruption Layer; crosses context boundary)
    │  EventAlertSchema
    ▼
AlertsFacade (notifications driving port)
    │
    ▼
SendEventAlertUseCase
    │  filtered subscriber list (notify_events=True, is_active=True)
    │  NotificationGenerator.format_event_alert(...)
    ▼
ITelegramGateway → AiogramGateway → Telegram API
```

---

## Core Context

### Domain

| Class | Description |
|---|---|
| `EventLogAgg` | Aggregate root for an event source. Owns event history and lifecycle. |
| `EventRecord` | Immutable record of a single detected event. |
| `EventSeverity` | Enum: INFO / WARNING / ERROR / CRITICAL |
| `TimeWindowVO` | Value object: active time window (supports midnight-crossing). |
| `SourceMetricsVO` | Aggregated counters (total, by severity). |

Domain events emitted by the aggregate:
- `EventDetectedEvent` — a new event was recorded
- `SourceDiscoveredEvent` — source became active for the first time
- `SourceDownEvent` — active source went inactive
- `SourceTimeoutEvent` — source silent within its active window

### Application Layer

Use cases (commands → side effects):

| Use Case | Triggered by |
|---|---|
| `ProcessEventUseCase` | DetectorManager callback |
| `AddSourceUseCase` | DetectorManager auto-registration |
| `UpdateSourceSettingsUseCase` | Web UI form |
| `ClearSourceHistoryUseCase` | Web UI button |
| `RemoveSourceUseCase` | Web UI button |
| `MarkSourceActiveUseCase` | DetectorManager lifecycle |
| `MarkSourceInactiveUseCase` | DetectorManager lifecycle |
| `CheckTimeoutsUseCase` | Background worker (every 30 s) |
| `TickHealthUseCase` | Direct last-seen update (skips full agg load) |
| `UpdateGlobalSettingsUseCase` | Dashboard form |

Queries (read-only):
- `GetDashboardQuery` — all sources with summary metrics
- `GetSourceDetailsQuery` — full aggregate
- `GetSourceStatsQuery` — stats DTO with uptime
- `GetActiveSourcesListQuery` / `GetInactiveSourcesListQuery`

### Detector Layer

```
NotificationDetector (ABC)
    run(on_event: OnEventCallback) -> None   ← implement this
    stop() -> None                           ← optional, for cleanup

MockDetector                                 ← ships with template
    Emits random events every 5-15s for 3 fake sources
    Periodically simulates a source going down

DetectorManager
    Bridges detector callbacks → use cases
    Auto-registers new source IDs via AddSourceUseCase
    Manages asyncio task lifecycle (start / stop)
```

---

## Notifications Context

### Domain

| Class | Description |
|---|---|
| `TelegramConfigAgg` | Singleton: stores bot token. |
| `TelegramSubscriberEnt` | A Telegram subscriber with three notification preference flags. |

### Application Layer

Alert use cases (`SendEventAlertUseCase`, `SendTimeoutAlertUseCase`, etc.) each:
1. Fetch the right filtered subscriber list (e.g. `get_active_for_events()`)
2. Call `NotificationGenerator.format_*()` to produce the message text
3. Broadcast to all matching subscribers via `ITelegramGateway`

### NotificationGenerator

Located at `src/notifications/ports/driving/alerts_facade.py`.

```python
class NotificationGenerator(ABC):
    def format_event_alert(self, source_name, severity, title, detail) -> str: ...
    def format_timeout_alert(self, source_name, last_seen) -> str: ...
    def format_source_discovered(self, source_name, discovered_at) -> str: ...
    def format_source_down(self, source_name, stopped_at) -> str: ...
```

`DefaultGenerator` ships with sensible HTML templates.
Subclass to customise any or all methods.

---

## Anti-Corruption Layer (ACL)

`src/core/ports/driven/notification_acl.py`

Translates core domain events → notifications facade schemas.
Ensures the `core` context never imports `notifications` domain objects.

---

## Background Worker

`src/root/entrypoints/worker.py`

Runs on app startup (as an asyncio Task):
1. Creates and starts `DetectorManager` (with `MockDetector`)
2. Starts `telegram_supervisor` (polls for token, restarts on change)
3. Calls `CheckTimeoutsUseCase` every 30 seconds

---

## Dependency Injection

[Dishka](https://dishka.readthedocs.io/) manages all dependencies.

Scopes:
- `APP` — created once per process (engine, session factory, bot token config, NotificationGenerator)
- `REQUEST` — created per HTTP request or background task call (DB session, repos, use cases, facades)

DI providers:
- `SharedProvider` — engine, session, sessionmaker
- `CoreProvider` — core repos, UCs, queries, facades
- `NotificationsProvider` — notification repos, UCs, queries, facades, generator

Container built in `src/root/container.py`, mounted on the Litestar app in `src/root/entrypoints/api.py`.
