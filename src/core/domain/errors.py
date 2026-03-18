from shared.generics.errors import DomainError


class DuplicateEventError(DomainError):
    def __init__(self, source_id: str, event_id: str):
        super().__init__(f"Event {event_id} already recorded for source {source_id}")
        self.source_id = source_id
        self.event_id = event_id


class SourceNotFoundError(DomainError):
    def __init__(self, source_id: str):
        super().__init__(f"Source '{source_id}' not found")
        self.source_id = source_id
