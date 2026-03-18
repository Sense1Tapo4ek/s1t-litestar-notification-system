from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from core.domain import EventSeverity


class TgSourceCardSchema(BaseModel):
    id: str
    display_name: str
    is_active: bool
    total_events: int
    error_count: int
    last_seen_ts: Optional[datetime]


class TgSourceStatsSchema(BaseModel):
    id: str
    display_name: str
    is_active: bool
    total_events: int
    info_count: int
    warning_count: int
    error_count: int
    critical_count: int
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
    uptime_seconds: Optional[int]
