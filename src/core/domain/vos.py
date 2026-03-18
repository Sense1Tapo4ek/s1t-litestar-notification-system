from dataclasses import dataclass
from datetime import time
from decimal import Decimal

from shared.generics import EventSeverity  # noqa: F401 -- re-exported for convenience

__all__ = ["EventSeverity", "TimeWindowVO", "SourceMetricsVO"]


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeWindowVO:
    """
    Active time window for a source.
    Used to suppress timeout alerts outside of expected operating hours.
    Supports midnight-crossing ranges (e.g. 23:00–07:00).
    """
    start_time: time
    end_time: time

    def is_active_at(self, current_time: time) -> bool:
        if self.start_time <= self.end_time:
            return self.start_time <= current_time <= self.end_time
        return current_time >= self.start_time or current_time <= self.end_time


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceMetricsVO:
    """Aggregated statistics for an event source."""
    total_events: int
    info_count: int
    warning_count: int
    error_count: int
    critical_count: int

    @property
    def error_rate(self) -> Decimal:
        if self.total_events == 0:
            return Decimal("0")
        return Decimal(self.error_count + self.critical_count) / Decimal(self.total_events) * Decimal("100")
