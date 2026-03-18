from shared.generics.errors import AppError


class SourceNotFoundError(AppError):
    def __init__(self, source_id: str):
        super().__init__(f"Source '{source_id}' not found in registry")
        self.source_id = source_id
