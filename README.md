# s1t-litestar-notification-system

A production-ready template for building event-driven notification systems with:

- **[Litestar](https://litestar.dev/)** — async Python web framework (SSR + JSON API)
- **[Aiogram 3](https://docs.aiogram.dev/)** — Telegram bot integration
- **[Dishka](https://dishka.readthedocs.io/)** — typed dependency injection
- **SQLite / SQLAlchemy** — async ORM, zero-config storage
- **Japandi UI** — warm minimalist design system

Two simple extension points replace all domain-specific logic:

| Abstraction | What it does | Where to put yours |
|---|---|---|
| `NotificationDetector` | Long-running loop that emits raw events | `src/core/ports/driving/detector/` |
| `NotificationGenerator` | Formats domain events into Telegram messages | `src/notifications/ports/driving/alerts_facade.py` |

The template ships with a `MockDetector` that generates fake events every 5–15 s so the UI is live immediately after `uv run`.

---

## Quick Start

```bash
# 1. Clone or copy the template
git clone https://github.com/your-org/s1t-litestar-notification-system.git
cd s1t-litestar-notification-system

# 2. Create venv and install
uv venv && source .venv/bin/activate
uv pip install -e .

# 3. Create storage directory
mkdir -p storage

# 4. Run
PYTHONPATH=src uvicorn root.entrypoints.api:create_app --factory --reload

# Visit http://127.0.0.1:8000
```

Within ~10 seconds, the MockDetector will register three fake sources
(**payment-service**, **email-worker**, **data-pipeline**) and start emitting events.

---

## Environment Variables

Copy `.env.example` → `.env`:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Python log level |
| `CORE_DB_URL` | `sqlite+aiosqlite:///storage/app.sqlite` | SQLite path |
| `NOTIFICATIONS_API_TIMEOUT_SECONDS` | `10` | Telegram HTTP timeout |

---

## Docker

```bash
# Build and run
docker compose up --build

# Stop
docker compose down
```

---

## Telegram Bot Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) → get the token
2. Open the app admin page: `http://localhost:8000/admin`
3. Click **Set Token** → paste your token → **Save**
4. The polling supervisor detects the token and starts within 10 s
5. Open Telegram → send `/start` to your bot

**Available bot commands:**

| Command | Description |
|---|---|
| `/start` | Subscribe to notifications |
| `/sources` | List all event sources |
| `/stale` | Show inactive sources |
| `/settings` | Manage notification preferences |

---

## Extending

### Add a real event source

Create a subclass of `NotificationDetector`:

```python
# src/core/ports/driving/detector/my_detector.py
from core.ports.driving.detector.base_detector import NotificationDetector, OnEventCallback
from core.domain import EventSeverity
from datetime import datetime, timezone
from uuid import uuid4

class MyDetector(NotificationDetector):
    async def run(self, on_event: OnEventCallback) -> None:
        async for event in my_event_stream():
            await on_event(
                source_id="my-service",
                event_id=str(uuid4()),
                severity=EventSeverity.ERROR if event.is_error else EventSeverity.INFO,
                title=event.message[:120],
                detail=event.raw,
                timestamp=datetime.now(timezone.utc),
            )

    async def stop(self) -> None:
        my_event_stream.close()
```

Then replace `MockDetector` with `MyDetector` in `src/root/entrypoints/worker.py`:

```python
from core.ports.driving.detector.my_detector import MyDetector
# ...
detector = MyDetector()
```

### Customise notification messages

Subclass `NotificationGenerator` and register it in `src/notifications/provider.py`:

```python
class MyGenerator(NotificationGenerator):
    def format_event_alert(self, source_name, severity, title, detail) -> str:
        return f"🔔 [{source_name}] {title}"
    # implement other methods...

# In NotificationsProvider:
@provide(scope=Scope.APP)
def provide_notification_generator(self) -> NotificationGenerator:
    return MyGenerator()
```

---

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for a full description of the S-DDD layers.

---

## Project Layout

```
src/
  core/               ← main bounded context
    domain/           ← EventLogAgg, EventRecord, domain events
    app/              ← use cases, queries, interfaces
    ports/
      driving/        ← SourceUIFacade, CoreTelegramFacade, NotificationDetector
      driven/         ← repos, NotificationACL
    adapters/
      driving/        ← web views (SSR), telegram handlers
      driven/         ← ORM models
  notifications/      ← Telegram notification context
    domain/           ← TelegramConfigAgg, TelegramSubscriberEnt
    app/              ← alert use cases, subscriber management
    ports/
      driving/        ← AlertsFacade + NotificationGenerator, AdminUIFacade
      driven/         ← sqlite repos
    adapters/
      driving/        ← admin web views, telegram /start /settings
      driven/         ← AiogramGateway, ORM models
  shared/             ← config, logger, DI provider, static files, templates
  root/               ← composition root, entrypoints
```
