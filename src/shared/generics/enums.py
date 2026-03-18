from enum import Enum


class EventSeverity(str, Enum):
    """
    Shared kernel enum used by both core and notifications contexts.
    Stored as a plain string in the database.
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
