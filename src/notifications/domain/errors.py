from shared.generics.errors import DomainError


class TelegramNotConfiguredError(DomainError):
    def __init__(self) -> None:
        super().__init__("Telegram bot is not configured. Set a token via the admin UI.")


class SubscriberNotFoundError(DomainError):
    def __init__(self, chat_id: int) -> None:
        super().__init__(f"Subscriber {chat_id} not found")
        self.chat_id = chat_id
