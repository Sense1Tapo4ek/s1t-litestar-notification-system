from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class TelegramSubscriberEnt:
    chat_id: int
    username: str
    is_active: bool = True
    notify_events: bool = True
    notify_timeouts: bool = True
    notify_services: bool = True

    def toggle(self) -> None:
        self.is_active = not self.is_active
