# Extending the Notification System

This guide covers the most common extension scenarios.

---

## 1. Connecting a Real Event Source

Replace `MockDetector` with your own `NotificationDetector` subclass.

### Step 1 — Implement the detector

```python
# src/core/ports/driving/detector/my_service_detector.py
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from core.domain import EventSeverity
from core.ports.driving.detector.base_detector import NotificationDetector, OnEventCallback


class MyServiceDetector(NotificationDetector):
    """
    Example: poll a REST health endpoint every 60 s and emit events.
    """

    def __init__(self, endpoint: str) -> None:
        self._endpoint = endpoint
        self._stop = asyncio.Event()

    async def run(self, on_event: OnEventCallback) -> None:
        import httpx
        async with httpx.AsyncClient() as client:
            while not self._stop.is_set():
                try:
                    resp = await client.get(self._endpoint, timeout=5)
                    severity = EventSeverity.INFO if resp.is_success else EventSeverity.ERROR
                    title = f"Health check {resp.status_code}"
                    detail = resp.text[:200] if not resp.is_success else None
                except Exception as exc:
                    severity = EventSeverity.CRITICAL
                    title = "Health check failed"
                    detail = str(exc)

                await on_event(
                    source_id="my-service",
                    event_id=str(uuid4()),
                    severity=severity,
                    title=title,
                    detail=detail,
                    timestamp=datetime.now(timezone.utc),
                )
                await asyncio.sleep(60)

    async def stop(self) -> None:
        self._stop.set()
```

### Step 2 — Register in the worker

Edit `src/root/entrypoints/worker.py`:

```python
from core.ports.driving.detector.my_service_detector import MyServiceDetector

detector = MyServiceDetector(endpoint="https://my-service/health")
```

### Step 3 — (Optional) Add configuration

Add the endpoint URL to `src/shared/config.py` or `src/core/config.py` and read it via Pydantic Settings.

---

## 2. Customising Telegram Messages

Subclass `NotificationGenerator` to change how events appear in chats.

```python
# src/notifications/ports/driving/my_generator.py
from datetime import datetime
from core.domain import EventSeverity
from notifications.ports.driving.alerts_facade import NotificationGenerator


class MyGenerator(NotificationGenerator):

    def format_event_alert(self, source_name, severity, title, detail) -> str:
        icon = {"info": "🟢", "warning": "🟡", "error": "🔴", "critical": "💀"}.get(severity, "•")
        text = f"{icon} <b>{source_name.upper()}</b>: {title}"
        if detail:
            text += f"\n<pre>{detail[:300]}</pre>"
        return text

    def format_timeout_alert(self, source_name, last_seen) -> str:
        return (
            f"⏱ <b>{source_name}</b> — no events!\n"
            f"Last seen: {last_seen.strftime('%H:%M UTC')}"
        )

    def format_source_discovered(self, source_name, discovered_at) -> str:
        return f"🆕 Source online: <b>{source_name}</b>"

    def format_source_down(self, source_name, stopped_at) -> str:
        return f"🔴 Source offline: <b>{source_name}</b>"
```

Register it in `src/notifications/provider.py`:

```python
from notifications.ports.driving.my_generator import MyGenerator

@provide(scope=Scope.APP)
def provide_notification_generator(self) -> NotificationGenerator:
    return MyGenerator()
```

---

## 3. Adding a New Bounded Context

If your domain grows large, you can add a third context (e.g., `alerting/`) following the same pattern:

```
src/
  alerting/
    domain/
    app/
      interfaces/
      use_cases/
      queries/
    ports/
      driving/
      driven/
    adapters/
      driving/
      driven/
    config.py
    provider.py
```

Rules:
- Never import from another context's `domain/` or `app/` layer directly
- Communicate via facade interfaces or domain events
- Register your new `Provider` in `src/root/container.py`

---

## 4. Adding Telegram Commands

Add a new handler in `src/core/adapters/driving/telegram/handlers.py`:

```python
@router.message(Command("summary"))
async def cmd_summary(message: Message, facade: FromDishka[CoreTelegramFacade]) -> None:
    sources = await facade.list_sources()
    total = len(sources)
    active = sum(1 for s in sources if s.is_active)
    await message.reply(f"📊 <b>Summary</b>\nTotal: {total} | Active: {active}", parse_mode="HTML")
```

Register the command in `src/root/entrypoints/telegram.py`:

```python
BotCommand(command="summary", description="Show system summary"),
```

---

## 5. Multiple Detectors

`DetectorManager` manages one detector. To run multiple detectors concurrently, create multiple `DetectorManager` instances in `worker.py`:

```python
managers = [
    DetectorManager(detector=ServiceADetector(), ...),
    DetectorManager(detector=ServiceBDetector(), ...),
]
for m in managers:
    m.start()
```

Each detector's `on_event` callback is independent and thread-safe (uses the same `AddSourceUseCase` / `ProcessEventUseCase`).

---

## 6. Persistent Configuration

The `GlobalSettingsModel` in the `core` context stores key-value pairs in SQLite.
Extend it to persist any per-process configuration that should survive restarts:

```python
# In SqliteGlobalSettingsRepo
async def get_my_setting(self) -> str:
    return await self._get("my_key") or "default"

async def set_my_setting(self, value: str) -> None:
    await self._set("my_key", value)
```
